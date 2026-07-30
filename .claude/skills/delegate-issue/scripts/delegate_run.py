#!/usr/bin/env -S uv run
"""
Run a delegate agent in the background with monitoring and status tracking.

Usage (launcher):
  python delegate_run.py --prompt "<task>" [--model sonnet] [--repo <path>] [--slug <name>]
                         [--effort medium] [--timeout 2700]

Usage (worker, internal):
  python delegate_run.py --worker --slug <slug> --prompt "<task>" --model <model>
                         --delegates-dir <path> [--repo <path>] [--effort <level>] [--timeout <s>]
"""
import argparse
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Tope de reloj por delegate. Sin esto, proc.wait() no tiene timeout y un
# delegate colgado corre indefinido facturando tokens sin que nada lo note.
DEFAULT_TIMEOUT_S = 45 * 60


def is_wsl():
    try:
        return "microsoft" in Path("/proc/version").read_text().lower()
    except Exception:
        return False


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


def run_worker(slug, prompt, model, repo, effort, delegates_dir, timeout_s):
    """Worker mode: run the agent and track it. This process stays alive until agent exits."""
    delegate_dir = delegates_dir / slug
    delegate_dir.mkdir(parents=True, exist_ok=True)

    log_file = delegate_dir / "output.log"
    status_file = delegate_dir / "status.json"

    cwd = os.path.expanduser(repo) if repo else os.getcwd()

    # Write full prompt to file — avoids arg-parser failures when prompt starts with "---"
    # (YAML frontmatter or markdown separators look like CLI flags to some parsers)
    prompt_path = delegate_dir / "prompt.txt"
    prompt_path.write_text(prompt, encoding="utf-8")
    bootstrap = (
        f"Your full task prompt is in: {prompt_path}\n"
        f"Read that file first, then execute every instruction in it exactly."
    )

    claude_bin = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
    stdbuf = shutil.which("stdbuf")
    base_cmd = [claude_bin, "-p", bootstrap, "--model", model, "--dangerously-skip-permissions", "--effort", effort]
    cmd = ([stdbuf, "-oL", "-eL"] + base_cmd) if stdbuf else base_cmd

    started_at = datetime.now().isoformat()
    status = {
        "slug": slug,
        "status": "running",
        "model": model,
        "effort": effort,
        "timeout_s": timeout_s,
        "repo": cwd,
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

    # Wall-clock cap. Without it a stuck delegate runs forever: proc.wait() has
    # no timeout, and nothing else in the pipeline would notice. This is a cost
    # guard, not a security one — a runaway agent bills tokens until killed.
    timed_out = False
    try:
        exit_code = proc.wait(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        timed_out = True
        proc.terminate()  # SIGTERM: let it flush its log
        try:
            exit_code = proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
            exit_code = proc.wait()

    finished_at = datetime.now().isoformat()

    started = datetime.fromisoformat(started_at)
    finished = datetime.fromisoformat(finished_at)
    duration_s = int((finished - started).total_seconds())
    duration = f"{duration_s // 60}m {duration_s % 60}s"

    if timed_out:
        final_status = "timed-out"
    elif exit_code == 0:
        final_status = "completed"
    elif exit_code < 0:
        final_status = "killed"  # -15 SIGTERM · -9 SIGKILL
    else:
        final_status = "failed"

    status["status"] = final_status
    status["finished_at"] = finished_at
    status["exit_code"] = exit_code
    status["duration"] = duration
    status_file.write_text(json.dumps(status, indent=2))

    # Append to inbox for UserPromptSubmit hook to surface.
    # fsync ensures the write is durable before the hook reads on next prompt.
    inbox_file = delegates_dir / "inbox.md"
    icon = {"completed": "✓", "timed-out": "⏱"}.get(final_status, "✗")
    entry = f"- {icon} **{slug}** {final_status} ({duration}, exit: {exit_code}) — {prompt[:100]}\n"
    try:
        with open(inbox_file, "a", encoding="utf-8") as f:
            f.write(entry)
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        print(f"[delegate_run] WARNING: failed to write to inbox {inbox_file}: {e}", file=sys.stderr)

    # Audible notification
    beep_done(final_status == "completed")


def launch_worker(slug, prompt, model, repo, effort, delegates_dir, timeout_s):
    """Launcher mode: spawn worker as detached background process, return immediately."""
    script = Path(__file__).resolve()
    cmd = [
        sys.executable,
        str(script),
        "--worker",
        "--slug", slug,
        "--prompt", prompt,
        "--model", model,
        "--effort", effort,
        "--timeout", str(timeout_s),
        "--delegates-dir", str(delegates_dir),
    ]
    if repo:
        cmd += ["--repo", repo]

    kwargs = {}
    if platform.system() == "Windows":
        # CREATE_NO_WINDOW prevents a blank terminal from popping up.
        # CREATE_NEW_PROCESS_GROUP ensures the worker survives the parent exiting.
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen(cmd, close_fds=True, **kwargs)

    log_path = delegates_dir / slug / "output.log"
    print(f"Delegate '{slug}' started (background)")
    print(f"Log:     {log_path}")
    print(f"Monitor: python delegate_monitor.py {slug}")
    print(f"Kill:    python delegate_kill.py {slug}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true", help="Internal: run in worker mode")
    parser.add_argument("--slug", help="Unique slug (auto-generated if omitted)")
    parser.add_argument("--prompt", required=True, help="Task prompt for the agent")
    parser.add_argument("--model", default="sonnet", help="Model alias (opus/sonnet/haiku)")
    parser.add_argument("--repo", help="Repository path to run in")
    parser.add_argument("--effort", default="medium", choices=["low", "medium", "high", "max"],
                        help="Effort level: low (quick tasks) · medium (default) · high (complex) · max (architecture)")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S,
                        help=f"Tope de tiempo en segundos (default {DEFAULT_TIMEOUT_S} = "
                             f"{DEFAULT_TIMEOUT_S // 60} min). Al vencer, se mata el delegate.")
    parser.add_argument("--delegates-dir", help="Override delegates directory")
    args = parser.parse_args()

    delegates_dir = Path(args.delegates_dir) if args.delegates_dir else get_delegates_dir()
    slug = args.slug or (slugify(args.prompt[:40]) + "-" + str(int(time.time()))[-6:])

    if args.worker:
        run_worker(slug, args.prompt, args.model, args.repo, args.effort, delegates_dir, args.timeout)
    else:
        launch_worker(slug, args.prompt, args.model, args.repo, args.effort, delegates_dir, args.timeout)


if __name__ == "__main__":
    main()
