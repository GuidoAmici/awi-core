#!/usr/bin/env -S uv run
"""
Kill a running delegate agent.

Usage:
  python delegate_kill.py <slug>
"""
import argparse
import json
import os
import platform
import subprocess
from pathlib import Path


def get_delegates_dir():
    cwd = Path(os.getcwd())
    for p in [cwd] + list(cwd.parents):
        if (p / ".claude").exists():
            return p / ".claude" / "tmp" / "delegates"
    return Path.home() / ".claude" / "tmp" / "delegates"


def kill_delegate(delegates_dir: Path, slug: str) -> bool:
    delegate_dir = delegates_dir / slug
    status_file = delegate_dir / "status.json"

    if not status_file.exists():
        print(f"No delegate found: {slug}")
        return False

    status = json.loads(status_file.read_text())

    if status.get("status") != "running":
        print(f"Delegate '{slug}' is not running (status: {status.get('status')})")
        return False

    pid = status.get("pid")
    if not pid:
        print(f"No PID recorded for delegate '{slug}'")
        return False

    if platform.system() == "Windows":
        result = subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"Killed delegate '{slug}' and its process tree (PID: {pid})")
        else:
            print(f"taskkill output: {result.stdout.strip()} {result.stderr.strip()}")
    else:
        import os
        import signal
        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            print(f"Sent SIGTERM to process group of '{slug}' (PID: {pid})")
        except ProcessLookupError:
            print(f"Process {pid} not found (may have already exited)")

    status["status"] = "killed"
    status_file.write_text(json.dumps(status, indent=2))
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("slug", help="Delegate slug to kill")
    parser.add_argument("--delegates-dir", help="Override delegates directory")
    args = parser.parse_args()

    delegates_dir = Path(args.delegates_dir) if args.delegates_dir else get_delegates_dir()
    kill_delegate(delegates_dir, args.slug)


if __name__ == "__main__":
    main()
