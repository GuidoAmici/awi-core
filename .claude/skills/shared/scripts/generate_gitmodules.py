#!/usr/bin/env python3
"""Generate .gitmodules from current-user.json + user-submodules.json.

.gitmodules is ephemeral — never committed, always regenerated.
Call write_gitmodules(awi_root) from any skill or hook.
"""

import json
import sys
from pathlib import Path


def _section(entries: dict, header: str, comment: str) -> list[str]:
    if not entries:
        return []
    lines = [f"# ─── {header} {'─' * max(0, 76 - len(header))}",
             f"# {comment}", ""]
    for entry in entries.values():
        path = entry["path"]
        lines.append(f'[submodule "{path}"]')
        lines.append(f"\tpath = {path}")
        lines.append(f"\turl = {entry['url']}")
        lines.append(f"\tbranch = {entry.get('branch', 'only')}")
        if entry.get("upstream"):
            lines.append("\tupstream = true")
        lines.append("")
    return lines


def generate(awi_root: Path) -> str:
    """Return .gitmodules file content for the current user."""
    users_dir = awi_root / "_data" / "users"
    current_user_file = users_dir / "current-user.json"

    if not current_user_file.exists():
        raise FileNotFoundError("_data/users/current-user.json not found — run /awi-user to log in")

    current_user = json.loads(current_user_file.read_text())
    github_id    = str(current_user["github-id"])
    login        = current_user["login"]
    user_repo    = current_user.get("user_repo", f"{login}/my-awi-user")

    submodules_file = users_dir / github_id / "user-submodules.json"
    raw = json.loads(submodules_file.read_text()) if submodules_file.exists() else {}

    active = {k: v for k, v in raw.items() if v.get("active", False)}
    orgs   = {k: v for k, v in active.items() if v.get("path", "").startswith("_data/organizations/")}
    system = {k: v for k, v in active.items() if not v.get("path", "").startswith("_data/organizations/")}

    lines: list[str] = []
    lines += _section(orgs, "Entities",
        "One repo per company or person — agenda/, documentation/, codebase/.")
    lines += _section(system, "Workframe",
        "Structural framework repos — shared scaffolding or engine dependencies.")

    # Current user submodule is always last (resolved from current-user.json, not user-submodules.json)
    user_path = f"_data/users/{github_id}"
    lines += [
        "# ─── Workflow ─────────────────────────────────────────────────────────────────",
        "# Automation and tooling repos — the current user's workspace.",
        "",
        f'[submodule "{user_path}"]',
        f"\tpath = {user_path}",
        f"\turl = https://github.com/{user_repo}.git",
        "\tbranch = only",
        "",
    ]

    return "\n".join(lines)


def write_gitmodules(awi_root: Path) -> None:
    """Regenerate .gitmodules at awi_root."""
    (awi_root / ".gitmodules").write_text(generate(awi_root))


if __name__ == "__main__":
    awi_root = Path(__file__).resolve().parents[4]
    try:
        write_gitmodules(awi_root)
        print(".gitmodules regenerated.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
