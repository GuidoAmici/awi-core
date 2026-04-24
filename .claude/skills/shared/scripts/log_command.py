#!/usr/bin/env python3
"""Append a skill invocation to the current user's command log.

Usage:
    python3 log_command.py <command> <outcome>

Outcomes:
    completed  — skill ran to its natural end
    skipped    — operator cancelled or a prerequisite gate stopped execution
    errored    — a step failed unexpectedly

Resolves the user via _data/users/current-user.json.
Log written to _data/users/<github-id>/command-log.jsonl.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import USERS_DIR, CURRENT_USER

CURRENT_USER_FILE = CURRENT_USER
VALID_OUTCOMES = {"completed", "skipped", "errored"}


def resolve_github_id() -> str:
    """Read github-id from current-user.json."""
    if not CURRENT_USER_FILE.exists():
        raise FileNotFoundError(
            f"current-user.json not found at {CURRENT_USER_FILE}. "
            "Run /awi-user first."
        )

    data = json.loads(CURRENT_USER_FILE.read_text())
    github_id = data.get("github-id")
    if not github_id:
        raise ValueError("github-id not found in current-user.json")
    return str(github_id)


def log_command(command: str, outcome: str) -> None:
    github_id = resolve_github_id()

    log_dir = USERS_DIR / github_id
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "command-log.jsonl"

    entry = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M"),
        "command": command,
        "outcome": outcome,
    }

    with log_file.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def main():
    if len(sys.argv) != 3:
        print("Usage: log_command.py <command> <outcome>", file=sys.stderr)
        print(f"Valid outcomes: {', '.join(sorted(VALID_OUTCOMES))}", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]
    outcome = sys.argv[2]

    if outcome not in VALID_OUTCOMES:
        print(
            f"Invalid outcome '{outcome}'. Valid: {', '.join(sorted(VALID_OUTCOMES))}",
            file=sys.stderr,
        )
        sys.exit(1)

    log_command(command, outcome)


if __name__ == "__main__":
    main()
