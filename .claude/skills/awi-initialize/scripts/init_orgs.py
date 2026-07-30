#!/usr/bin/env python3
"""Materialise the repos the current operator wants on disk.

Reads user-submodules.json plus each org's codebases.json and clones whatever is
missing. Nothing here is a submodule: no gitlinks, no .gitmodules, no
`git submodule` calls. See ADR 0009.

Cloning happens in two passes because an org's codebases.json only becomes
readable once the org workspace itself is on disk.

An entry that is inactive but still mounted is never deleted — under this model
that directory is ordinary data, not a submodule checkout, so removing it is a
plain rm -rf with no gitlink to restore it from. The script reports those and
lets the operator decide one by one.

Exit codes:
  0  Everything active is on disk, nothing pending.
  1  Hard error.
  2  Nothing active, but inactive entries exist.  Stdout: INACTIVE: <names>
  3  Nothing registered at all.                   Stdout: NO_ORGS
  4  Actives are fine, but inactive entries are still mounted.
     Stdout: MOUNTED_INACTIVE: <name>\t<path> per line.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared" / "scripts"))
from paths import AWI_ROOT
from manifest import (
    Repo,
    active_entries,
    inactive_entries,
    is_mounted,
    load_submodules,
    materialise_target,
    plan,
)


def run_pass(repos: list[Repo], errors: list[str]) -> int:
    """Materialise every repo in `repos`. Returns how many were newly cloned."""
    cloned = 0
    for repo in repos:
        label = repo.name if not repo.is_codebase else f"{repo.parent}/{repo.name}"
        print(f"  → {label}...", end=" ", flush=True)
        status, err = materialise_target(repo.path, repo.url, repo.branch, repo.rev)
        if status == "cloned":
            print(f"cloned ({repo.rev or repo.branch})")
            cloned += 1
        elif status == "present":
            print("already on disk" + (f" at {repo.rev}" if repo.is_pinned else ""))
        elif status == "drifted":
            # Un repo pinneado en otro commit es drift: se reporta y no se
            # corrige en silencio. Alinearlo es un acto deliberado (ADR 0012).
            print("DRIFT")
            print(f"    ⚠ {err}", file=sys.stderr)
        else:
            print("FAILED")
            print(f"    ✗ {err}", file=sys.stderr)
            errors.append(label)
    return cloned


def main() -> int:
    try:
        raw, _github_id, _user_repo = load_submodules(AWI_ROOT)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if not raw:
        print("NO_ORGS")
        return 3

    active = active_entries(raw)
    inactive = inactive_entries(raw)

    if not active:
        print(f"INACTIVE: {', '.join(inactive)}")
        return 2

    errors: list[str] = []

    # Pass 1 — orgs, system repos and the operator's own repo.
    try:
        repos, warnings = plan(AWI_ROOT)
    except Exception as e:
        print(f"Error reading manifests: {e}", file=sys.stderr)
        return 1

    top = [r for r in repos if not r.is_codebase]
    print(f"Materialising {len(top)} workspace repo(s):\n")
    run_pass(top, errors)

    # Pass 2 — codebases. Re-planned, because the org workspaces cloned above
    # are what carry the codebases.json this pass depends on.
    try:
        repos, warnings = plan(AWI_ROOT)
    except Exception as e:
        print(f"Error reading manifests: {e}", file=sys.stderr)
        return 1

    codebases = [r for r in repos if r.is_codebase]
    if codebases:
        print(f"\nMaterialising {len(codebases)} codebase(s):\n")
        run_pass(codebases, errors)

    for w in warnings:
        print(f"  ⚠ {w}", file=sys.stderr)

    if errors:
        print(f"\n{len(errors)} repo(s) failed: {', '.join(errors)}", file=sys.stderr)
        return 1

    total = len(top) + len(codebases)
    print(f"\nAll {total} repo(s) on disk.")

    # Inactive but still mounted — reported, never removed.
    mounted = [
        (name, entry.get("path", ""))
        for name, entry in inactive.items()
        if is_mounted(AWI_ROOT / entry.get("path", ""))
    ]
    if mounted:
        print()
        for name, path in mounted:
            print(f"MOUNTED_INACTIVE: {name}\t{path}")
        return 4

    return 0


if __name__ == "__main__":
    sys.exit(main())
