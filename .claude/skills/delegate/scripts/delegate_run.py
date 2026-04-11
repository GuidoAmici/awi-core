#!/usr/bin/env -S uv run
"""
Run a delegate agent in the background with monitoring and status tracking.

Usage (launcher):
  python delegate_run.py --prompt "<task>" [--model opus] [--repo <path>] [--slug <name>] [--budget 0.50]

Usage (worker, internal):
  python delegate_run.py --worker --slug <slug> --prompt "<task>" --model <model> --delegates-dir <path> [--repo <path>] [--budget <usd>]
"""
import argparse
import json
import os
import platform
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def get_delegates_dir():
    cwd = Path(os.getcwd())
    for p in [cwd] + list(cwd.parents):
        if (p / ".claude").exists():
            return p / ".claude" / "tmp" / "delegates"
    return Path.home() / ".claude" / "tmp" / "delegates"


def slugify(text):
    slug = re.sub(r"[^a-z0-9-]", "-", text.lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:36]


def beep_done(success):
    try:
        if success:
            subprocess.run(
                ["powershell", "-Command", "[Console]::Beep(784,100); [Console]::Beep(1047,200)"],
                capture_output=True, timeout=3,
            )
        else:
            subprocess.run(
                ["powershell", "-Command", "[Console]::Beep(300,200); [Console]::Beep(250,300)"],
                capture_output=True, timeout=3,
            )
    except Exception:
        pass


def run_worker(slug, prompt, model, repo, budget, delegates_dir):
    """Worker mode: run the agent and track it. This process stays alive until agent exits."""
    delegate_dir = delegates_dir / slug
    delegate_dir.mkdir(parents=True, exist_ok=True)

    log_file = delegate_dir / "output.log"
    status_file = delegate_dir / "status.json"

    cwd = os.path.expanduser(repo) if repo else os.getcwd()

    cmd = ["claude", "-p", prompt, "--model", model, "--dangerously-skip-permissions"]
    if budget:
        cmd += ["--max-budget-usd", str(budget)]

    started_at = datetime.now().isoformat()
    status = {
        "slug": slug,
        "status": "running",
        "model": model,
        "repo": cwd,
        "budget_usd": budget,
        "prompt_preview": prompt[:300],
        "started_at": started_at,
        "finished_at": None,
        "exit_code": None,
        "pid": None,
        "duration": None,
    }
    status_file.write_text(json.dumps(status, indent=2))

    with open(log_file, "w", buffering=1, encoding="utf-8", errors="replace") as log:
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=log,
            stderr=subprocess.STDOUT,
            env={**os.environ, "CLAUDE_DELEGATED": "1"},
        )

    status["pid"] = proc.pid
    status_file.write_text(json.dumps(status, indent=2))

    exit_code = proc.wait()
    finished_at = datetime.now().isoformat()

    started = datetime.fromisoformat(started_at)
    finished = datetime.fromisoformat(finished_at)
    duration_s = int((finished - started).total_seconds())
    duration = f"{duration_s // 60}m {duration_s % 60}s"

    if exit_code == 0:
        final_status = "completed"
    elif exit_code in (-15, -9, 1):
        # -15 = SIGTERM (killed), -9 = SIGKILL, 1 = budget exceeded or interrupted
        final_status = "killed" if exit_code < 0 else "failed"
    else:
        final_status = "failed"

    status["status"] = final_status
    status["finished_at"] = finished_at
    status["exit_code"] = exit_code
    status["duration"] = duration
    status_file.write_text(json.dumps(status, indent=2))

    # Append to inbox for UserPromptSubmit hook to surface
    inbox_file = delegates_dir / "inbox.md"
    icon = "✓" if final_status == "completed" else "✗"
    entry = f"- {icon} **{slug}** {final_status} ({duration}, exit: {exit_code}) — {prompt[:100]}\n"
    with open(inbox_file, "a", encoding="utf-8") as f:
        f.write(entry)

    # Audible notification
    beep_done(final_status == "completed")


def launch_worker(slug, prompt, model, repo, budget, delegates_dir, visible=False):
    """Launcher mode: spawn worker as detached background process, return immediately."""
    script = Path(__file__).resolve()
    cmd = [
        sys.executable,
        str(script),
        "--worker",
        "--slug", slug,
        "--prompt", prompt,
        "--model", model,
        "--delegates-dir", str(delegates_dir),
    ]
    if repo:
        cmd += ["--repo", repo]
    if budget is not None:
        cmd += ["--budget", str(budget)]

    if visible and platform.system() == "Windows":
        # Open a new tab in Windows Terminal so the user can watch live output.
        worker_cmd = " ".join(f'"{a}"' if " " in a else a for a in cmd)
        subprocess.Popen(
            ["wt", "--title", slug, "new-tab", "--", "cmd", "/k", worker_cmd],
            close_fds=True,
        )
    else:
        kwargs = {}
        if platform.system() == "Windows":
            # CREATE_NO_WINDOW prevents a blank terminal from popping up.
            # CREATE_NEW_PROCESS_GROUP ensures the worker survives the parent exiting.
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kwargs["start_new_session"] = True
        subprocess.Popen(cmd, close_fds=True, **kwargs)

    log_path = delegates_dir / slug / "output.log"
    mode = "visible tab" if visible else "background"
    print(f"Delegate '{slug}' started ({mode})")
    print(f"Log:     {log_path}")
    print(f"Monitor: python delegate_monitor.py {slug}")
    print(f"Kill:    python delegate_kill.py {slug}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true", help="Internal: run in worker mode")
    parser.add_argument("--slug", help="Unique slug (auto-generated if omitted)")
    parser.add_argument("--prompt", required=True, help="Task prompt for the agent")
    parser.add_argument("--model", default="opus", help="Model alias (opus/sonnet/haiku)")
    parser.add_argument("--repo", help="Repository path to run in")
    parser.add_argument("--budget", type=float, default=0.50, help="Max spend in USD (default: 0.50)")
    parser.add_argument("--delegates-dir", help="Override delegates directory")
    parser.add_argument("--visible", action="store_true", help="Open in a new Windows Terminal tab instead of running silently")
    args = parser.parse_args()

    delegates_dir = Path(args.delegates_dir) if args.delegates_dir else get_delegates_dir()
    slug = args.slug or (slugify(args.prompt[:40]) + "-" + str(int(time.time()))[-6:])

    if args.worker:
        run_worker(slug, args.prompt, args.model, args.repo, args.budget, delegates_dir)
    else:
        launch_worker(slug, args.prompt, args.model, args.repo, args.budget, delegates_dir, visible=args.visible)


if __name__ == "__main__":
    main()
