#!/usr/bin/env python3
"""Initialize AWI submodules for the current user.

Reads user-submodules.json, regenerates .gitmodules, then:
  - Inits every active entry
  - Deinits (after commit+push) every inactive entry that's mounted on disk

Exit codes:
  0  All active submodules initialized successfully.
  1  Hard error (commit/push failure, git failure, etc.).
  2  No submodules active, but inactive ones exist.  Stdout: INACTIVE: <names>
  3  No submodules registered at all.               Stdout: NO_ORGS
"""

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared" / "scripts"))
from paths import AWI_ROOT, USERS_DIR, USER_SUBMODULES_FILE
from current_user import resolve_github_id
from generate_gitmodules import write_gitmodules


# ── Git helpers ───────────────────────────────────────────────────────────────

def git(args: list[str], cwd: Path = AWI_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)


def is_mounted(path: Path) -> bool:
    """True if the submodule working tree has content."""
    return path.exists() and any(path.iterdir())


def commit_and_push(path: Path, name: str) -> str | None:
    """Commit any dirty state and push. Returns error string on failure, None on success."""
    status = git(["status", "--porcelain"], cwd=path)
    if status.stdout.strip():
        rc = git(["add", "-A"], cwd=path)
        if rc.returncode != 0:
            return f"{name}: git add failed — {rc.stderr.strip()}"
        rc = git(["commit", "-m", "cos: sync - stage local changes before deinit"], cwd=path)
        if rc.returncode != 0:
            return f"{name}: commit failed — {rc.stderr.strip()}"

    rc = git(["push"], cwd=path)
    if rc.returncode != 0:
        return f"{name}: push failed — {rc.stderr.strip()}"
    return None


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    github_id      = resolve_github_id()
    submodules_file = USERS_DIR / github_id / USER_SUBMODULES_FILE

    if not submodules_file.exists():
        print("NO_ORGS")
        return 3

    raw = json.loads(submodules_file.read_text())
    if not raw:
        print("NO_ORGS")
        return 3

    active   = {k: v for k, v in raw.items() if v.get("active", False)}
    inactive = {k: v for k, v in raw.items() if not v.get("active", False)}

    if not active:
        print(f"INACTIVE: {', '.join(inactive)}")
        return 2

    # Regenerate .gitmodules from user-submodules.json + current-user.json
    try:
        write_gitmodules(AWI_ROOT)
        print(".gitmodules regenerated.\n")
    except Exception as e:
        print(f"Error regenerating .gitmodules: {e}", file=sys.stderr)
        return 1

    errors: list[str] = []

    # Deinit inactive entries that are still mounted
    for name, entry in inactive.items():
        path = AWI_ROOT / entry.get("path", "")
        if not is_mounted(path):
            continue
        print(f"  deinit {name}...", end=" ", flush=True)
        err = commit_and_push(path, name)
        if err:
            print("FAILED")
            print(f"    ✗ {err}", file=sys.stderr)
            errors.append(name)
            continue
        rc = git(["submodule", "deinit", "-f", entry["path"]])
        if rc.returncode != 0:
            print("FAILED")
            print(f"    ✗ deinit failed: {rc.stderr.strip()}", file=sys.stderr)
            errors.append(name)
        else:
            print("done")

    if errors:
        print(f"\n{len(errors)} submodule(s) failed to deinit — aborting init.", file=sys.stderr)
        return 1

    # Init active entries
    names = list(active.keys())
    print(f"Initializing {len(active)} submodule(s): {', '.join(names)}\n")

    for name, entry in active.items():
        print(f"  → {name}...", end=" ", flush=True)
        rc = git(["submodule", "update", "--init", "--recursive", entry["path"]])
        if rc.returncode == 0:
            print("done")
        else:
            print("FAILED")
            print(f"    ✗ {rc.stderr.strip()}", file=sys.stderr)
            errors.append(name)

    if errors:
        print(f"\n{len(errors)} submodule(s) failed: {', '.join(errors)}")
        return 1

    print(f"\nAll {len(active)} submodule(s) initialized.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
