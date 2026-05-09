#!/usr/bin/env python3
"""Toggle AWI org submodules on/off with persistent state per user.

State is stored in _data/users/<github-id>/active-orgs.json.
Current user is resolved from _data/users/current-user.json.

Usage:
    python3 toggle_org.py toggle <name> [--url <url>]   # flip state (--url required for new orgs)
    python3 toggle_org.py on <name> [--url <url>]       # explicitly enable
    python3 toggle_org.py off <name>                    # explicitly disable
    python3 toggle_org.py status                        # show all orgs and state
"""

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared" / "scripts"))
from paths import AWI_ROOT, USERS_DIR, ORGANIZATIONS_RELDIR
from current_user import resolve_github_id


def resolve_state_file() -> Path:
    return USERS_DIR / resolve_github_id() / "active-orgs.json"


def load_state(state_file: Path) -> dict:
    if not state_file.exists():
        return {}
    return json.loads(state_file.read_text())


def save_state(state_file: Path, state: dict) -> None:
    state_file.write_text(json.dumps(state, indent=2) + "\n")


def is_in_gitmodules(name: str) -> bool:
    gitmodules = AWI_ROOT / ".gitmodules"
    if not gitmodules.exists():
        return False
    return f"_data/organizations/{name}" in gitmodules.read_text()


def add_submodule(name: str, url: str) -> int:
    result = subprocess.run(
        ["git", "submodule", "add", url, f"{ORGANIZATIONS_RELDIR}/{name}"],
        cwd=AWI_ROOT,
    )
    return result.returncode


def is_active_on_disk(name: str) -> bool:
    """True if the submodule working directory has content (is initialized)."""
    org_path = AWI_ROOT / ORGANIZATIONS_RELDIR / name
    return org_path.exists() and any(org_path.iterdir())


def sync_git(name: str, active: bool) -> int:
    if active:
        result = subprocess.run(
            ["git", "submodule", "update", "--init", "--recursive",
             f"{ORGANIZATIONS_RELDIR}/{name}"],
            cwd=AWI_ROOT,
        )
    else:
        if not is_active_on_disk(name):
            print(f"'{name}' already off.")
            return 0
        result = subprocess.run(
            ["git", "submodule", "deinit", "-f",
             f"{ORGANIZATIONS_RELDIR}/{name}"],
            cwd=AWI_ROOT,
        )
    return result.returncode


def ensure_registered(name: str, url: str | None, state: dict) -> int:
    """Register org in .gitmodules if not present. Returns non-zero on failure."""
    if not is_in_gitmodules(name):
        if not url:
            print(f"Error: '{name}' not in .gitmodules. Provide --url <url> to register it.",
                  file=sys.stderr)
            return 1
        rc = add_submodule(name, url)
        if rc != 0:
            return rc
    # Ensure entry exists in state with URL
    if name not in state:
        state[name] = {"url": url or "", "active": False}
    elif url:
        state[name]["url"] = url
    return 0


def cmd_toggle(name: str, url: str | None) -> int:
    state_file = resolve_state_file()
    state = load_state(state_file)

    rc = ensure_registered(name, url, state)
    if rc != 0:
        return rc

    new_active = not state[name].get("active", False)
    state[name]["active"] = new_active
    save_state(state_file, state)
    label = "on" if new_active else "off"
    print(f"'{name}' toggled {label}.")
    return sync_git(name, new_active)


def cmd_set(name: str, active: bool, url: str | None) -> int:
    state_file = resolve_state_file()
    state = load_state(state_file)

    rc = ensure_registered(name, url, state)
    if rc != 0:
        return rc

    state[name]["active"] = active
    save_state(state_file, state)
    label = "on" if active else "off"
    print(f"'{name}' set {label}.")
    return sync_git(name, active)


def cmd_status() -> int:
    state_file = resolve_state_file()
    state = load_state(state_file)

    if not state:
        print("No orgs registered. Use: toggle_org.py toggle <name> --url <url>")
        return 0

    print("Org toggle state:\n")
    for name, entry in state.items():
        flag = entry.get("active", False)
        label = "on " if flag else "off"
        print(f"  {label}  _data/organizations/{name}")
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    action = sys.argv[1]

    # Parse optional --url <url>
    url = None
    args = sys.argv[2:]
    if "--url" in args:
        idx = args.index("--url")
        if idx + 1 < len(args):
            url = args[idx + 1]
            args = args[:idx] + args[idx + 2:]

    if action == "status":
        return cmd_status()

    if not args:
        print(f"Error: '{action}' requires an org name.", file=sys.stderr)
        return 1

    name = args[0]

    if action == "toggle":
        return cmd_toggle(name, url)
    elif action == "on":
        return cmd_set(name, True, url)
    elif action == "off":
        return cmd_set(name, False, url)
    else:
        print(f"Unknown action '{action}'. Use: toggle, on, off, status", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
