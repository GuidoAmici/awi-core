#!/usr/bin/env -S uv run
"""
Monitor background delegate agents.

Usage:
  python delegate_monitor.py              # list all delegates
  python delegate_monitor.py <slug>       # show status + tail logs
  python delegate_monitor.py <slug> --tail 100
"""
import argparse
import json
import os
from datetime import datetime
from pathlib import Path


STUCK_THRESHOLD_S = 90  # seconds without log output before flagging as stuck


def get_delegates_dir():
    cwd = Path(os.getcwd())
    for p in [cwd] + list(cwd.parents):
        if (p / ".claude").exists():
            return p / ".claude" / "tmp" / "delegates"
    return Path.home() / ".claude" / "tmp" / "delegates"


def is_stuck(log_file: Path, status: dict) -> bool:
    if status.get("status") != "running":
        return False
    # Flag as stuck if log is empty after threshold (never started writing)
    if not log_file.exists() or log_file.stat().st_size == 0:
        started = status.get("started_at")
        if not started:
            return False
        age_s = datetime.now().timestamp() - datetime.fromisoformat(started).timestamp()
        return age_s > STUCK_THRESHOLD_S
    idle_s = datetime.now().timestamp() - log_file.stat().st_mtime
    return idle_s > STUCK_THRESHOLD_S


def idle_seconds(log_file: Path) -> int:
    if not log_file.exists():
        return 0
    return int(datetime.now().timestamp() - log_file.stat().st_mtime)


STATUS_ICONS = {
    "running": "~",
    "completed": "OK",
    "failed": "!!",
    "killed": "XX",
}


def show_all(delegates_dir: Path):
    if not delegates_dir.exists():
        print("No delegates directory found.")
        return

    dirs = sorted(
        [d for d in delegates_dir.iterdir() if d.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not dirs:
        print("No delegates found.")
        return

    print(f"{'':2} {'SLUG':<38} {'STATUS':<10} {'STARTED':<20} {'DURATION':<10} {'MODEL'}")
    print("-" * 100)

    for d in dirs:
        sf = d / "status.json"
        if not sf.exists():
            continue
        s = json.loads(sf.read_text())
        icon = STATUS_ICONS.get(s.get("status"), "?")
        stuck = is_stuck(d / "output.log", s)
        stuck_warn = " ⚠STUCK" if stuck else ""
        started = s.get("started_at", "")[:19].replace("T", " ")
        duration = s.get("duration") or ("running" if s.get("status") == "running" else "?")
        model = s.get("model", "?")
        print(f"{icon}  {s['slug']:<38} {s.get('status','?'):<10} {started:<20} {duration:<10} {model}{stuck_warn}")

    # Show inbox
    inbox = delegates_dir / "inbox.md"
    if inbox.exists():
        content = inbox.read_text(encoding="utf-8").strip()
        if content:
            print(f"\n--- Pending notifications (inbox) ---")
            print(content)


def show_delegate(delegates_dir: Path, slug: str, tail_lines: int):
    delegate_dir = delegates_dir / slug
    if not delegate_dir.exists():
        print(f"No delegate found: {slug}")
        return

    sf = delegate_dir / "status.json"
    log_file = delegate_dir / "output.log"

    if sf.exists():
        s = json.loads(sf.read_text())
        stuck = is_stuck(log_file, s)
        icon = STATUS_ICONS.get(s.get("status"), "?")

        print(f"=== {icon} {slug} ===")
        print(f"  Status:   {s.get('status')}")
        print(f"  Model:    {s.get('model')}  |  Budget: ${s.get('budget_usd', '?')}")
        print(f"  Repo:     {s.get('repo')}")
        print(f"  Started:  {s.get('started_at', '')[:19].replace('T', ' ')}")
        if s.get("finished_at"):
            print(f"  Finished: {s.get('finished_at', '')[:19].replace('T', ' ')}  ({s.get('duration')})")
        elif s.get("status") == "running":
            idle = idle_seconds(log_file)
            print(f"  Idle:     {idle}s since last output")
        print(f"  PID:      {s.get('pid')}")
        print(f"  Prompt:   {s.get('prompt_preview', '')[:120]}")
        if stuck:
            print(f"\n  ⚠ WARNING: No log output for {STUCK_THRESHOLD_S}+ seconds — agent may be stuck")
            print(f"  Run: python delegate_kill.py {slug}  to interrupt")

    if log_file.exists():
        lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
        print(f"\n=== Log (last {tail_lines} of {len(lines)} lines) ===")
        print("\n".join(lines[-tail_lines:]))
    else:
        print("\n(no log file yet)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("slug", nargs="?", help="Delegate slug to inspect (omit to list all)")
    parser.add_argument("--tail", type=int, default=60, help="Lines of log to show (default: 60)")
    parser.add_argument("--delegates-dir", help="Override delegates directory")
    args = parser.parse_args()

    delegates_dir = Path(args.delegates_dir) if args.delegates_dir else get_delegates_dir()

    if args.slug:
        show_delegate(delegates_dir, args.slug, args.tail)
    else:
        show_all(delegates_dir)


if __name__ == "__main__":
    main()
