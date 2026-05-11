#!/usr/bin/env python3
"""Toggle AWI submodules on/off with persistent state per user.

State is stored in _data/users/<github-id>/user-submodules.json.
Current user is resolved from _data/users/current-user.json.

Usage:
    python3 toggle_submodule.py toggle <name>    # flip state
    python3 toggle_submodule.py on <name>        # explicitly enable
    python3 toggle_submodule.py off <name>       # explicitly disable
    python3 toggle_submodule.py status           # list all entries
"""

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared" / "scripts"))
from paths import AWI_ROOT, USERS_DIR, USER_SUBMODULES_FILE
from current_user import resolve_github_id
from generate_gitmodules import write_gitmodules


def git(args: list[str], cwd: Path = AWI_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)


def state_file() -> Path:
    return USERS_DIR / resolve_github_id() / USER_SUBMODULES_FILE


def load(f: Path) -> dict:
    return json.loads(f.read_text()) if f.exists() else {}


def save(f: Path, state: dict) -> None:
    f.write_text(json.dumps(state, indent=2) + "\n")


def is_mounted(entry: dict) -> bool:
    path = AWI_ROOT / entry.get("path", "")
    return path.exists() and any(path.iterdir())


def commit_and_push(name: str, path: Path) -> str | None:
    status = git(["status", "--porcelain"], cwd=path)
    if status.stdout.strip():
        git(["add", "-A"], cwd=path)
        rc = git(["commit", "-m", f"cos: sync - stage local changes before deinit {name}"], cwd=path)
        if rc.returncode != 0:
            return f"commit failed: {rc.stderr.strip()}"
    rc = git(["push"], cwd=path)
    if rc.returncode != 0:
        return f"push failed: {rc.stderr.strip()}"
    return None


def sync_git(name: str, entry: dict, active: bool) -> int:
    path_rel = entry.get("path", "")
    path_abs = AWI_ROOT / path_rel

    if active:
        rc = git(["submodule", "update", "--init", "--recursive", path_rel])
        if rc.returncode != 0:
            print(f"  ✗ init failed: {rc.stderr.strip()}", file=sys.stderr)
        return rc.returncode
    else:
        if not is_mounted(entry):
            print(f"  '{name}' already off disk.")
            return 0
        err = commit_and_push(name, path_abs)
        if err:
            print(f"  ✗ {err}", file=sys.stderr)
            return 1
        rc = git(["submodule", "deinit", "-f", path_rel])
        if rc.returncode != 0:
            print(f"  ✗ deinit failed: {rc.stderr.strip()}", file=sys.stderr)
        return rc.returncode


def apply(name: str, new_active: bool) -> int:
    f = state_file()
    state = load(f)

    if name not in state:
        print(f"Error: '{name}' not found in user-submodules.json.", file=sys.stderr)
        print("Add it manually with the required fields (url, path, branch) then retry.")
        return 1

    state[name]["active"] = new_active
    save(f, state)
    label = "on" if new_active else "off"
    print(f"'{name}' set {label}.")

    try:
        write_gitmodules(AWI_ROOT)
        print(".gitmodules regenerated.")
    except Exception as e:
        print(f"Warning: .gitmodules not updated — {e}", file=sys.stderr)

    return sync_git(name, state[name], new_active)


def cmd_status() -> int:
    f = state_file()
    state = load(f)
    if not state:
        print("No submodules registered in user-submodules.json.")
        return 0
    print("Submodule state:\n")
    for name, entry in state.items():
        flag   = entry.get("active", False)
        label  = "on " if flag else "off"
        path   = entry.get("path", "?")
        mnt    = " [mounted]" if is_mounted(entry) else ""
        print(f"  {label}  {path}{mnt}")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    action = sys.argv[1]

    if action == "status":
        return cmd_status()

    if len(sys.argv) < 3:
        print(f"Error: '{action}' requires a submodule name.", file=sys.stderr)
        return 1

    name = sys.argv[2]

    if action == "toggle":
        f     = state_file()
        state = load(f)
        if name not in state:
            print(f"Error: '{name}' not in user-submodules.json.", file=sys.stderr)
            return 1
        return apply(name, not state[name].get("active", False))
    elif action == "on":
        return apply(name, True)
    elif action == "off":
        return apply(name, False)
    else:
        print(f"Unknown action '{action}'. Use: toggle, on, off, status", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
