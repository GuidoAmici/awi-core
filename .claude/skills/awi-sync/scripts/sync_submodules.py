#!/usr/bin/env python3
"""
/awi-sync — Scan, sync, and report all AWI submodules (direct + nested).

For each submodule:
  1. Check if cloned locally
  2. Remove .gitkeep from populated folders
  3. Commit any uncommitted changes (git add -A)
  4. Checkout tracked branch and pull
  5. Push to remote

After submodules: sync AWI root itself, then mirror drift to awi-core dev-claude.

Outputs a human-readable report and updates _data/submodules.md.
"""

import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared" / "scripts"))
from paths import AWI_ROOT, SUBMODULES_MD

from sync_status import collect_core_files, collect_local_files, md5, parse_whitelist, read_kind

REGISTRY_PATH = SUBMODULES_MD

# Nested display names (parent_label, relative_path) -> short Mermaid node ID.
# AWI-level entries are built dynamically in build_node_id_map() — no hardcoding needed there.
# Update this dict when adding repos inside a client submodule.
_NESTED_NODE_IDS: dict[tuple[str, str], str] = {
    ("newhaze", "codebase/newhaze-api"): "api",
    ("newhaze", "codebase/newhaze-b2b-panel"): "b2b",
    ("newhaze", "codebase/newhaze-consumer-panel"): "consumer",
    ("newhaze", "codebase/newhaze-intern-panel"): "intern",
    ("newhaze", "codebase/newhaze-learn"): "learn",
    ("newhaze", "codebase/newhaze-ui"): "ui",
    ("newhaze", "codebase/newhaze-website"): "website",
    ("newhaze", "documentation/wiki"): "wiki",
}


def build_node_id_map() -> dict[tuple[str, str], str]:
    """Build the full node ID map dynamically.

    AWI-level: derived from .gitmodules — basename of path, except _data/users/* → "user".
    Nested: from _NESTED_NODE_IDS (configured manually per client).
    Falls back to basename if not in map (see scan()).
    """
    mapping: dict[tuple[str, str], str] = {}
    for m in parse_gitmodules(AWI_ROOT / ".gitmodules"):
        path = m.get("path", m["name"])
        if path.startswith("_data/users/"):
            node_id = "user"
        else:
            node_id = path.split("/")[-1]
        mapping[("AWI", path)] = node_id
    mapping.update(_NESTED_NODE_IDS)
    return mapping


# ── Data model ────────────────────────────────────────────────────────────────


@dataclass
class SubmoduleResult:
    name: str
    path: str           # relative to parent repo root
    abs_path: Path      # absolute on disk
    parent: str         # "AWI" or parent submodule label
    parent_abs: Path    # absolute path of parent repo root
    remote_url: str
    node_id: str        # Mermaid node ID
    tracked_branch: str = "main"   # from .gitmodules branch =
    cloned: bool = False
    branch: Optional[str] = None
    pinned_sha: Optional[str] = None
    upstream: bool = False
    dirty: bool = False
    dirty_files: list = field(default_factory=list)
    committed: bool = False
    pushed: bool = False
    # ok | already_up_to_date | pulled | failed | not_cloned
    sync_status: str = "not_cloned"
    error: Optional[str] = None


# ── Git helpers ───────────────────────────────────────────────────────────────


def git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def get_pinned_sha(repo_root: Path, submodule_path: str) -> Optional[str]:
    """SHA the parent repo has pinned for this submodule path."""
    r = git(["ls-files", "--stage", "--", submodule_path], cwd=repo_root)
    for line in r.stdout.splitlines():
        if line.startswith("160000"):
            return line.split()[1][:8]
    return None


def is_valid_git_repo(path: Path) -> bool:
    r = git(["rev-parse", "--git-dir"], cwd=path)
    return r.returncode == 0


def in_nested_repo(file_path: Path, repo_root: Path) -> bool:
    """True if file_path is inside a nested git repo (submodule boundary)."""
    p = file_path.parent
    while p != repo_root:
        if (p / ".git").exists():
            return True
        p = p.parent
    return False


def clean_gitkeeps(repo_root: Path) -> None:
    """Remove .gitkeep from populated folders; create .gitkeep in empty folders."""
    for dirpath in repo_root.rglob("*"):
        if not dirpath.is_dir():
            continue
        if in_nested_repo(dirpath, repo_root):
            continue
        contents = list(dirpath.iterdir())
        non_gitkeep = [f for f in contents if f.name != ".gitkeep"]
        gitkeep = dirpath / ".gitkeep"
        if non_gitkeep:
            if gitkeep.exists():
                gitkeep.unlink()
        else:
            if not gitkeep.exists():
                gitkeep.touch()


# ── Submodule discovery ───────────────────────────────────────────────────────


def parse_gitmodules(path: Path) -> list[dict]:
    """Return list of {name, path, url} from a .gitmodules file."""
    if not path.exists():
        return []
    modules: list[dict] = []
    current: dict = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[submodule"):
            if current:
                modules.append(current)
            current = {"name": line.split('"')[1]}
        elif "=" in line and current is not None:
            key, _, val = line.partition("=")
            current[key.strip()] = val.strip()
    if current:
        modules.append(current)
    return modules


def scan() -> list[SubmoduleResult]:
    """Discover all submodules: AWI-level first, then nested inside each client."""
    results: list[SubmoduleResult] = []
    node_id_map = build_node_id_map()

    # AWI direct submodules
    awi_modules = parse_gitmodules(AWI_ROOT / ".gitmodules")
    for m in awi_modules:
        sub_path = m.get("path", m["name"])
        abs_path = AWI_ROOT / sub_path
        name = sub_path.split("/")[-1]
        node_id = node_id_map.get(("AWI", sub_path), name)
        results.append(SubmoduleResult(
            name=name,
            path=sub_path,
            abs_path=abs_path,
            parent="AWI",
            parent_abs=AWI_ROOT,
            remote_url=m.get("url", ""),
            node_id=node_id,
            pinned_sha=get_pinned_sha(AWI_ROOT, sub_path),
            tracked_branch=m.get("branch", "main"),
            upstream=m.get("upstream", "false").lower() == "true",
        ))

    # Nested submodules — scan each cloned client
    for parent in list(results):
        nested_path = parent.abs_path / ".gitmodules"
        if not nested_path.exists():
            continue
        for m in parse_gitmodules(nested_path):
            sub_path = m.get("path", m["name"])
            abs_path = parent.abs_path / sub_path
            name = sub_path.split("/")[-1]
            node_id = node_id_map.get((parent.name, sub_path), name)
            results.append(SubmoduleResult(
                name=name,
                path=sub_path,
                abs_path=abs_path,
                parent=parent.name,
                parent_abs=parent.abs_path,
                remote_url=m.get("url", ""),
                node_id=node_id,
                pinned_sha=get_pinned_sha(parent.abs_path, sub_path),
                tracked_branch=m.get("branch", "main"),
            ))

    return results


# ── Sync logic ────────────────────────────────────────────────────────────────


def sync_one(r: SubmoduleResult) -> SubmoduleResult:
    path = r.abs_path

    # Not on disk at all
    if not path.exists() or not (path / ".git").exists():
        r.cloned = False
        r.sync_status = "not_cloned"
        r.error = "Directory missing or not a git repo. Run: git submodule update --init"
        return r

    r.cloned = True

    # Validate git repo
    if not is_valid_git_repo(path):
        r.sync_status = "failed"
        r.error = "Broken .git reference — cannot run git commands here."
        return r

    # Current branch
    res = git(["branch", "--show-current"], cwd=path)
    r.branch = res.stdout.strip() or None  # None = detached HEAD

    # Remove .gitkeep from populated folders (stays within this repo boundary)
    clean_gitkeeps(path)

    # Uncommitted changes — commit everything
    res = git(["status", "--porcelain"], cwd=path)
    dirty_lines = [l for l in res.stdout.splitlines() if l.strip()]
    r.dirty = bool(dirty_lines)
    r.dirty_files = dirty_lines[:5]

    if r.dirty:
        git(["add", "-A"], cwd=path)
        res = git(["commit", "-m", "cos: sync - stage local changes"], cwd=path)
        if res.returncode != 0:
            r.sync_status = "failed"
            r.error = f"Commit failed: {res.stderr.strip()}"
            return r
        r.committed = True

    # Checkout tracked branch
    target = r.tracked_branch
    if r.branch != target:
        res = git(["checkout", target], cwd=path)
        if res.returncode != 0:
            r.sync_status = "failed"
            r.error = f"Cannot checkout {target}: {res.stderr.strip()}"
            return r
        r.branch = target

    # Pull
    res = git(["pull", "origin", target], cwd=path)
    if res.returncode != 0:
        r.sync_status = "failed"
        r.error = f"Pull failed: {res.stderr.strip()}"
        return r

    pulled = "Already up to date" not in res.stdout

    # Push (skip for upstream-only repos)
    if not r.upstream:
        res = git(["push", "origin", target], cwd=path)
        if res.returncode != 0:
            r.sync_status = "failed"
            r.error = f"Push failed: {res.stderr.strip()}"
            return r
        r.pushed = True

    r.sync_status = "pulled" if pulled else "already_up_to_date"
    return r


def sync_all(results: list[SubmoduleResult]) -> list[SubmoduleResult]:
    synced = []
    for r in results:
        r = sync_one(r)
        synced.append(r)
        _write_table_row(r)
    return synced


def sync_root() -> dict:
    """Sync the AWI root repo (commit + pull + push on current branch).
    Runs after submodules so updated submodule pointers are included.
    """
    path = AWI_ROOT
    result: dict = {"branch": None, "committed": False, "pushed": False,
                    "status": "already_up_to_date", "error": None}

    res = git(["branch", "--show-current"], cwd=path)
    branch = res.stdout.strip()
    result["branch"] = branch

    clean_gitkeeps(path)

    res = git(["status", "--porcelain"], cwd=path)
    dirty = [l for l in res.stdout.splitlines() if l.strip()]
    if dirty:
        git(["add", "-A"], cwd=path)
        res = git(["commit", "-m", "cos: sync - stage local changes"], cwd=path)
        if res.returncode != 0:
            result["status"] = "failed"
            result["error"] = f"Commit failed: {res.stderr.strip()}"
            return result
        result["committed"] = True

    res = git(["pull", "origin", branch], cwd=path)
    if res.returncode != 0:
        result["status"] = "failed"
        result["error"] = f"Pull failed: {res.stderr.strip()}"
        return result
    if "Already up to date" not in res.stdout:
        result["status"] = "pulled"

    res = git(["push", "origin", branch], cwd=path)
    if res.returncode != 0:
        result["status"] = "failed"
        result["error"] = f"Push failed: {res.stderr.strip()}"
        return result
    result["pushed"] = True

    return result


def sync_awi_core() -> dict:
    """Mirror drifted/missing whitelisted files from AWI to awi-core dev-claude."""
    result: dict = {"drift": [], "missing": [], "committed": False,
                    "pushed": False, "status": "ok", "error": None}

    public_repo_path = AWI_ROOT / ".claude" / "config" / "public-repo-path"
    core_root = AWI_ROOT / public_repo_path.read_text().strip()
    whitelist_path = AWI_ROOT / ".claude" / "config" / "public-whitelist"

    if not core_root.is_dir():
        result["status"] = "failed"
        result["error"] = f"awi-core not found at {core_root}"
        return result

    res = git(["checkout", "dev-claude"], cwd=core_root)
    if res.returncode != 0:
        result["status"] = "failed"
        result["error"] = f"Cannot checkout dev-claude: {res.stderr.strip()}"
        return result

    entries = parse_whitelist(whitelist_path)
    local_files = collect_local_files(AWI_ROOT, entries)
    core_files = collect_core_files(core_root)

    for rel, local_path in sorted(local_files.items()):
        if read_kind(local_path) == "context":
            continue
        if rel in core_files:
            if md5(local_path) != md5(core_files[rel]):
                result["drift"].append(rel)
                shutil.copy2(local_path, core_root / rel)
        else:
            result["missing"].append(rel)
            dest = core_root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(local_path, dest)

    if not result["drift"] and not result["missing"]:
        return result

    git(["add", "-A"], cwd=core_root)
    n = len(result["drift"]) + len(result["missing"])
    res = git(["commit", "-m", f"cos: sync - mirror {n} file(s) from AWI"], cwd=core_root)
    if res.returncode != 0:
        result["status"] = "failed"
        result["error"] = f"awi-core commit failed: {res.stderr.strip()}"
        return result
    result["committed"] = True

    res = git(["push", "origin", "dev-claude"], cwd=core_root)
    if res.returncode != 0:
        result["status"] = "failed"
        result["error"] = f"awi-core push failed: {res.stderr.strip()}"
        return result
    result["pushed"] = True
    result["status"] = "synced"

    return result


# ── Registry update ───────────────────────────────────────────────────────────


def mermaid_class(r: SubmoduleResult) -> str:
    if not r.cloned:
        return "danger"
    if r.sync_status == "failed":
        return "warning"
    return "safe"


def clone_status_label(r: SubmoduleResult) -> str:
    if not r.cloned:
        return "🔴 not cloned"
    branch = r.branch or "detached"
    if r.sync_status == "failed":
        return f"🟡 sync failed · {branch}"
    return f"🟢 cloned · {branch}"


def _write_table_row(r: SubmoduleResult) -> None:
    """Update the registry table row for a single submodule. Called after each sync."""
    if not REGISTRY_PATH.exists():
        return
    lines = REGISTRY_PATH.read_text().splitlines()
    local_path = str(r.abs_path.relative_to(AWI_ROOT))
    anchor = f"`{local_path}`"
    sha_cell = f" `{r.pinned_sha}` " if r.pinned_sha else " not indexed "
    status_cell = f" {clone_status_label(r)} "
    new_lines: list[str] = []
    for line in lines:
        if anchor in line and line.strip().startswith("|"):
            parts = line.split("|")
            if len(parts) >= 6:
                parts[-3] = sha_cell
                parts[-2] = status_cell
                line = "|".join(parts)
        new_lines.append(line)
    REGISTRY_PATH.write_text("\n".join(new_lines))


def update_registry(results: list[SubmoduleResult]) -> None:
    """Rebuild Mermaid class lines from all results. Called once after all syncs."""
    if not REGISTRY_PATH.exists():
        return

    lines = REGISTRY_PATH.read_text().splitlines()

    # ── Rebuild Mermaid class lines ──────────────────────────────────────────
    by_class: dict[str, list[str]] = {"safe": [], "warning": [], "danger": []}
    for r in results:
        by_class[mermaid_class(r)].append(r.node_id)

    new_class_lines = [
        f"    class {','.join(nodes)} {cls}"
        for cls, nodes in by_class.items()
        if nodes
    ]

    updated: list[str] = []
    class_inserted = False
    for line in lines:
        stripped = line.strip()
        is_class = stripped.startswith("class ") and any(
            s in stripped for s in (" safe", " warning", " danger")
        )
        if is_class:
            if not class_inserted:
                updated.extend(new_class_lines)
                class_inserted = True
        else:
            updated.append(line)

    REGISTRY_PATH.write_text("\n".join(updated))


# ── Report ────────────────────────────────────────────────────────────────────


STATUS_ICON = {
    "ok": "✓",
    "already_up_to_date": "✓",
    "pulled": "↓",
    "failed": "✗",
    "not_cloned": "✗",
}

STATUS_LABEL = {
    "ok": "up to date",
    "already_up_to_date": "up to date",
    "pulled": "pulled",
    "failed": "failed",
    "not_cloned": "not cloned",
}


def print_report(results: list[SubmoduleResult], root: dict, core: dict) -> int:
    ok = sum(1 for r in results if r.sync_status in ("ok", "already_up_to_date", "pulled"))
    failed = sum(1 for r in results if r.sync_status in ("failed", "not_cloned"))

    print()
    print("AWI Submodule Sync")
    print("─" * 52)

    # Root
    print("\n  [AWI root]")
    icon = STATUS_ICON.get(root["status"], "?")
    label = STATUS_LABEL.get(root["status"], root["status"])
    branch_str = f" · {root['branch']}" if root["branch"] else ""
    tags = (" [committed]" if root["committed"] else "") + (" [pushed]" if root["pushed"] else "")
    print(f"  {icon}  {'my-awi-instance':<36} {label}{branch_str}{tags}")
    if root["error"]:
        print(f"     → {root['error']}")
    if root["status"] == "failed":
        failed += 1

    # Submodules
    current_parent = None
    for r in results:
        if r.parent != current_parent:
            current_parent = r.parent
            print(f"\n  [{r.parent}]")

        icon = STATUS_ICON.get(r.sync_status, "?")
        label = STATUS_LABEL.get(r.sync_status, r.sync_status)
        indent = "    " if r.parent != "AWI" else "  "
        branch_str = f" · {r.branch}" if r.branch and r.cloned else ""
        tags = (
            (" [committed]" if r.committed else "")
            + (" [upstream]" if r.upstream else (" [pushed]" if r.pushed else ""))
        )
        print(f"{indent}{icon}  {r.name:<36} {label}{branch_str}{tags}")
        if r.error:
            print(f"{indent}   → {r.error}")

    # awi-core
    print("\n  [awi-core → dev-claude]")
    if core["status"] == "ok":
        print(f"  ✓  {'awi-core':<36} up to date")
    elif core["status"] == "synced":
        n_drift = len(core["drift"])
        n_missing = len(core["missing"])
        tags = (" [committed]" if core["committed"] else "") + (" [pushed]" if core["pushed"] else "")
        print(f"  ↓  {'awi-core':<36} {n_drift} drift, {n_missing} missing synced{tags}")
    elif core["status"] == "failed":
        print(f"  ✗  {'awi-core':<36} failed")
        print(f"     → {core['error']}")
        failed += 1

    print()
    print("─" * 52)
    print(f"✓ {ok} submodules synced   ✗ {failed} failed")
    print()
    print("_data/submodules.md updated.")
    print()

    return 1 if failed > 0 else 0


# ── Entry point ───────────────────────────────────────────────────────────────


def main() -> None:
    # 1. Sync submodules first
    results = scan()
    results = sync_all(results)
    update_registry(results)

    # 2. Sync AWI root (captures any submodule pointer updates)
    root = sync_root()

    # 3. Mirror to awi-core dev-claude
    core = sync_awi_core()

    exit_code = print_report(results, root, core)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
