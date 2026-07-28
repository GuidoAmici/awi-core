#!/usr/bin/env python3
"""Toggle which repos this operator wants on disk.

State lives in _data/users/<github-id>/user-submodules.json; the current user
comes from _data/users/current-user.json.

Two things can be toggled:

    <name>            an org workspace or system repo
    <org>/<codebase>  one codebase inside an org

Turning something on clones it. Turning it off records the choice and pushes any
local work, but never deletes the directory — nothing here is a submodule, so a
checkout is ordinary data with no gitlink to restore it from. See ADR 0009.

Usage:
    python3 toggle_submodule.py toggle <name>
    python3 toggle_submodule.py on <name>
    python3 toggle_submodule.py off <name>
    python3 toggle_submodule.py status
"""

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared" / "scripts"))
from paths import AWI_ROOT, USERS_DIR, USER_SUBMODULES_FILE
from current_user import resolve_github_id
from manifest import (
    CODEBASE_SUBDIR,
    active_codebases,
    entry_type,
    is_mounted,
    load_codebases,
    materialise_target,
)


def git(args: list[str], cwd: Path = AWI_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)


def state_file() -> Path:
    return USERS_DIR / resolve_github_id() / USER_SUBMODULES_FILE


def load(f: Path) -> dict:
    return json.loads(f.read_text()) if f.exists() else {}


def save(f: Path, state: dict) -> None:
    f.write_text(json.dumps(state, indent=2) + "\n")


def push_local_work(name: str, path: Path) -> str | None:
    """Commit and push anything uncommitted, so turning an entry off is safe."""
    if not (path / ".git").exists():
        return None
    status = git(["status", "--porcelain"], cwd=path)
    if status.stdout.strip():
        git(["add", "-A"], cwd=path)
        rc = git(
            ["commit", "-m", f"chore(sync): stage local work before {name} goes off"],
            cwd=path,
        )
        if rc.returncode != 0:
            return f"commit failed: {rc.stderr.strip()}"
    rc = git(["push"], cwd=path)
    if rc.returncode != 0:
        return f"push failed: {rc.stderr.strip()}"
    return None


# ── Target resolution ─────────────────────────────────────────────────────────

def resolve(state: dict, name: str) -> tuple[str, dict, str] | None:
    """Resolve `name` to (kind, entry, key). None if unknown.

    kind is "entry" for a top-level repo, "codebase" for <org>/<codebase>; in the
    codebase case `entry` is the owning org and `key` the codebase name.
    """
    if "/" in name:
        org_name, cb_name = name.split("/", 1)
        entry = state.get(org_name)
        if entry is None or entry_type(entry) != "org-workspace":
            return None
        return "codebase", entry, cb_name
    if name in state:
        return "entry", state[name], name
    return None


def codebase_path(entry: dict, cb_name: str) -> Path:
    return AWI_ROOT / entry["path"] / CODEBASE_SUBDIR / cb_name


def ensure_codebase_map(entry: dict) -> dict:
    """Turn the implicit "all codebases" into an explicit map.

    An org with no `codebases` key means the operator never curated it, so every
    codebase counts as on. Switching one off has to write that list down first,
    or the absent key would keep meaning "all" and undo the choice.
    """
    if entry.get("codebases") is None:
        declared = load_codebases(AWI_ROOT / entry["path"])
        entry["codebases"] = {n: {"active": True} for n in declared}
    return entry["codebases"]


def report_left_on_disk(label: str, path: Path) -> None:
    print(f"  '{label}' is off, but still on disk at {path.relative_to(AWI_ROOT)}.")
    print("  Local work is pushed. Delete the directory yourself if you want it gone.")


# ── Actions ───────────────────────────────────────────────────────────────────

def apply_entry(name: str, entry: dict, new_active: bool) -> int:
    entry["active"] = new_active
    path = AWI_ROOT / entry.get("path", "")

    if new_active:
        status, err = materialise_target(path, entry["url"], entry.get("branch", "only"))
        if status == "failed":
            print(f"  ✗ {err}", file=sys.stderr)
            return 1
        print(f"  {name}: {status}")
        return 0

    if not is_mounted(path):
        print(f"  '{name}' is not on disk — nothing to preserve.")
        return 0
    err = push_local_work(name, path)
    if err:
        print(f"  ✗ {err}", file=sys.stderr)
        return 1
    report_left_on_disk(name, path)
    return 0


def apply_codebase(org_name: str, entry: dict, cb_name: str, new_active: bool) -> int:
    declared = load_codebases(AWI_ROOT / entry["path"])
    if cb_name not in declared:
        print(
            f"Error: '{cb_name}' is not declared in {org_name}/codebases.json.",
            file=sys.stderr,
        )
        print(f"Declared: {', '.join(declared) or '(none)'}")
        return 1

    ensure_codebase_map(entry).setdefault(cb_name, {})["active"] = new_active

    path = codebase_path(entry, cb_name)
    spec = declared[cb_name]
    label = f"{org_name}/{cb_name}"

    if new_active:
        status, err = materialise_target(path, spec["url"], spec.get("branch", "main"))
        if status == "failed":
            print(f"  ✗ {err}", file=sys.stderr)
            return 1
        print(f"  {label}: {status}")
        return 0

    if not is_mounted(path):
        print(f"  '{label}' is not on disk — nothing to preserve.")
        return 0
    err = push_local_work(cb_name, path)
    if err:
        print(f"  ✗ {err}", file=sys.stderr)
        return 1
    report_left_on_disk(label, path)
    return 0


def apply(name: str, new_active: bool) -> int:
    f = state_file()
    state = load(f)

    target = resolve(state, name)
    if target is None:
        print(f"Error: '{name}' not found in user-submodules.json.", file=sys.stderr)
        print("Use <name> for an org or system repo, or <org>/<codebase> for a codebase.")
        return 1

    kind, entry, key = target
    if kind == "entry":
        rc = apply_entry(key, entry, new_active)
    else:
        rc = apply_codebase(name.split("/", 1)[0], entry, key, new_active)

    save(f, state)
    print(f"'{name}' set {'on' if new_active else 'off'}.")
    return rc


def current_state(state: dict, name: str) -> bool:
    target = resolve(state, name)
    if target is None:
        return False
    kind, entry, key = target
    if kind == "entry":
        return entry.get("active", False)
    wanted = active_codebases(entry)
    return wanted is None or key in wanted


def cmd_status() -> int:
    state = load(state_file())
    if not state:
        print("Nothing registered in user-submodules.json.")
        return 0

    print("Registered repos:\n")
    for name, entry in state.items():
        flag = "on " if entry.get("active", False) else "off"
        path = entry.get("path", "?")
        mnt = " [on disk]" if is_mounted(AWI_ROOT / path) else ""
        print(f"  {flag}  {name:<26} {path}{mnt}")

        if entry_type(entry) != "org-workspace":
            continue
        declared = load_codebases(AWI_ROOT / path)
        wanted = active_codebases(entry)
        for cb_name in declared:
            on = wanted is None or cb_name in wanted
            cb_flag = "on " if on else "off"
            cb_mnt = " [on disk]" if is_mounted(codebase_path(entry, cb_name)) else ""
            print(f"         {cb_flag}  {name}/{cb_name}{cb_mnt}")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    action = sys.argv[1]

    if action == "status":
        return cmd_status()

    if len(sys.argv) < 3:
        print(f"Error: '{action}' requires a name.", file=sys.stderr)
        return 1

    name = sys.argv[2]

    if action == "toggle":
        state = load(state_file())
        if resolve(state, name) is None:
            print(f"Error: '{name}' not in user-submodules.json.", file=sys.stderr)
            return 1
        return apply(name, not current_state(state, name))
    if action == "on":
        return apply(name, True)
    if action == "off":
        return apply(name, False)

    print(f"Unknown action '{action}'. Use: toggle, on, off, status", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
