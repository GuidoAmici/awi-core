#!/usr/bin/env python3
"""Initialize all toggled-on AWI org submodules.

Reads _data/users/<github-id>/active-orgs.json (resolved from current-user.json,
auto-created if missing) and for each active org:
  1. Registers the submodule in .gitmodules if not already present.
  2. Runs git submodule update --init --recursive.

Exit codes:
  0  All active orgs initialized successfully.
  1  Hard error (bad URL, git failure, etc.).
  2  No orgs active, but inactive ones exist.   Stdout: INACTIVE: <names>
  3  No orgs registered at all.                 Stdout: NO_ORGS
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


def is_in_gitmodules(name: str) -> bool:
    gitmodules = AWI_ROOT / ".gitmodules"
    if not gitmodules.exists():
        return False
    return f"_data/organizations/{name}" in gitmodules.read_text()


def main():
    state_file = resolve_state_file()

    # Auto-create empty state file if missing
    if not state_file.exists():
        state_file.write_text("{}\n")

    state = json.loads(state_file.read_text())

    active = [(name, entry) for name, entry in state.items() if entry.get("active", False)]
    inactive = [name for name, entry in state.items() if not entry.get("active", False)]

    if not active:
        if not state:
            print("NO_ORGS")
            return 3
        print(f"INACTIVE: {', '.join(inactive)}")
        return 2

    names = [name for name, _ in active]
    print(f"Initializing {len(active)} org(s): {', '.join(names)}\n")

    errors = []
    for name, entry in active:
        print(f"  → {name}...", end=" ", flush=True)

        # Register in .gitmodules if missing
        if not is_in_gitmodules(name):
            url = entry.get("url", "")
            if not url:
                print("SKIPPED (no URL in active-orgs.json)")
                errors.append(name)
                continue
            reg = subprocess.run(
                ["git", "submodule", "add", url, f"{ORGANIZATIONS_RELDIR}/{name}"],
                cwd=AWI_ROOT,
                capture_output=True,
                text=True,
            )
            if reg.returncode != 0:
                print("FAILED (submodule add)")
                errors.append(name)
                if reg.stderr:
                    print(f"    {reg.stderr.strip()}")
                continue

        # Initialize and checkout
        result = subprocess.run(
            ["git", "submodule", "update", "--init", "--recursive",
             f"{ORGANIZATIONS_RELDIR}/{name}"],
            cwd=AWI_ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("done")
        else:
            print("FAILED")
            errors.append(name)
            if result.stderr:
                print(f"    {result.stderr.strip()}")

    if errors:
        print(f"\n{len(errors)} org(s) failed: {', '.join(errors)}")
        return 1

    print(f"\nAll {len(active)} org(s) initialized.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
