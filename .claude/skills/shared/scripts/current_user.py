#!/usr/bin/env python3
"""Shared utility: resolve the current AWI user.

Auto-creates _data/users/current-user.json from gh auth state if missing.
"""

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import USERS_DIR


def resolve_github_id() -> str:
    """Return github-id string, auto-creating current-user.json if missing."""
    current_user_file = USERS_DIR / "current-user.json"

    if current_user_file.exists():
        return str(json.loads(current_user_file.read_text())["github-id"])

    # Auto-create from gh auth state
    result = subprocess.run(
        ["gh", "api", "user", "--jq", "{id: .id, login: .login}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("Error: not authenticated with GitHub. Run 'gh auth login' first.",
              file=sys.stderr)
        sys.exit(1)

    data = json.loads(result.stdout)
    record = {
        "user": f"_data/users/{data['id']}/",
        "github-id": str(data["id"]),
        "login": data["login"],
        "since": date.today().isoformat(),
    }
    current_user_file.write_text(json.dumps(record, indent=2) + "\n")
    print(f"Auto-created current-user.json for @{data['login']}", file=sys.stderr)
    return str(data["id"])
