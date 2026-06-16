#!/usr/bin/env python3
"""PreToolUse guard for gh auth switch / gh auth logout.

Reads tool input from stdin (JSON). If the Bash command is a gh auth
switch or logout, commits and pushes all dirty mounted submodules first.
Blocks the command (exit 2) if any commit or push fails.
"""

import json
import subprocess
import sys
from pathlib import Path

SHARED = Path(__file__).resolve().parents[1] / "skills" / "shared" / "scripts"
sys.path.insert(0, str(SHARED))
from paths import AWI_ROOT, USERS_DIR, USER_SUBMODULES_FILE
from current_user import resolve_github_id


def git(args: list[str], cwd: Path = AWI_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)


def mounted_submodule_paths() -> list[tuple[str, Path]]:
    """Return (name, abs_path) for all mounted submodules in user-submodules.json."""
    try:
        github_id = resolve_github_id()
    except SystemExit:
        return []
    submodules_file = USERS_DIR / github_id / USER_SUBMODULES_FILE
    if not submodules_file.exists():
        return []
    raw = json.loads(submodules_file.read_text())
    results = []
    for name, entry in raw.items():
        path = AWI_ROOT / entry.get("path", "")
        if path.exists() and any(path.iterdir()):
            results.append((name, path))
    return results


def commit_and_push(name: str, path: Path) -> str | None:
    """Commit dirty state and push. Returns error message or None on success."""
    status = git(["status", "--porcelain"], cwd=path)
    if status.stdout.strip():
        git(["add", "-A"], cwd=path)
        rc = git(["commit", "-m", "cos: sync - stage local changes before auth switch"], cwd=path)
        if rc.returncode != 0:
            return f"{name}: commit failed — {rc.stderr.strip()}"
    rc = git(["push"], cwd=path)
    if rc.returncode != 0:
        return f"{name}: push failed — {rc.stderr.strip()}"
    return None


def block(reason: str) -> None:
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Bash":
        return

    command = data.get("tool_input", {}).get("command", "")
    is_switch  = "gh auth switch" in command
    is_logout  = "gh auth logout" in command
    if not is_switch and not is_logout:
        return

    action = "switch" if is_switch else "logout"
    mounted = mounted_submodule_paths()
    if not mounted:
        return  # nothing to protect

    errors = []
    for name, path in mounted:
        err = commit_and_push(name, path)
        if err:
            errors.append(err)

    if errors:
        joined = "\n".join(f"  • {e}" for e in errors)
        block(
            f"AWI blocked `gh auth {action}` — could not commit+push all submodules:\n"
            f"{joined}\n\n"
            f"Fix the errors above, then retry."
        )


if __name__ == "__main__":
    main()
