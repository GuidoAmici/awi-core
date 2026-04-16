#!/usr/bin/env python3
"""
/awi-sync — Scan, sync, and report all AWI submodules (direct + nested).

For each submodule:
  1. Check if cloned locally
  2. Check for uncommitted changes (skips sync if dirty)
  3. Checkout main and pull
  4. Report result

Outputs a human-readable report and updates _data/submodules.md.
"""

import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

AWI_ROOT = Path(__file__).resolve().parents[4]
REGISTRY_PATH = AWI_ROOT / "_data" / "submodules.md"

# Maps (parent_label, submodule_path) -> Mermaid node ID
NODE_ID_MAP: dict[tuple[str, str], str] = {
    ("AWI", "_data/clients/newhaze"): "newhaze",
    ("AWI", "_data/clients/awi-core"): "awi-core",
    ("AWI", "_data/clients/afin"): "afin",
    ("AWI", "_data/users/42481462"): "user",
    ("newhaze", "codebase/newhaze-api"): "api",
    ("newhaze", "codebase/newhaze-b2b-panel"): "b2b",
    ("newhaze", "codebase/newhaze-consumer-panel"): "consumer",
    ("newhaze", "codebase/newhaze-intern-panel"): "intern",
    ("newhaze", "codebase/newhaze-learn"): "learn",
    ("newhaze", "codebase/newhaze-ui"): "ui",
    ("newhaze", "codebase/newhaze-website"): "website",
    ("newhaze", "documentation/wiki"): "wiki",
}


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
    dirty: bool = False
    dirty_files: list = field(default_factory=list)
    # ok | already_up_to_date | pulled | skipped | failed | not_cloned
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

    # AWI direct submodules
    awi_modules = parse_gitmodules(AWI_ROOT / ".gitmodules")
    for m in awi_modules:
        sub_path = m.get("path", m["name"])
        abs_path = AWI_ROOT / sub_path
        name = sub_path.split("/")[-1]
        node_id = NODE_ID_MAP.get(("AWI", sub_path), name)
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
            node_id = NODE_ID_MAP.get((parent.name, sub_path), name)
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

    # Uncommitted changes
    res = git(["status", "--porcelain"], cwd=path)
    dirty_lines = [l for l in res.stdout.splitlines() if l.strip()]
    r.dirty = bool(dirty_lines)
    r.dirty_files = dirty_lines[:5]

    if r.dirty:
        r.sync_status = "skipped"
        r.error = (
            f"{len(dirty_lines)} uncommitted file(s). "
            "Commit or stash before syncing."
        )
        return r

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

    r.sync_status = (
        "already_up_to_date"
        if "Already up to date" in res.stdout
        else "pulled"
    )
    return r


def sync_all(results: list[SubmoduleResult]) -> list[SubmoduleResult]:
    return [sync_one(r) for r in results]


# ── Registry update ───────────────────────────────────────────────────────────


def mermaid_class(r: SubmoduleResult) -> str:
    if not r.cloned:
        return "danger"
    if r.dirty or r.sync_status in ("failed", "skipped"):
        return "warning"
    return "safe"


def clone_status_label(r: SubmoduleResult) -> str:
    if not r.cloned:
        return "🔴 not cloned"
    branch = r.branch or "detached"
    if r.sync_status == "skipped":
        return f"🟡 dirty · {branch}"
    if r.sync_status == "failed":
        return f"🟡 sync failed · {branch}"
    return f"🟢 cloned · {branch}"


def update_registry(results: list[SubmoduleResult]) -> None:
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

    lines = updated

    # ── Update table rows (Pinned SHA + Clone status) ────────────────────────
    for r in results:
        local_path = str(r.abs_path.relative_to(AWI_ROOT))
        anchor = f"`{local_path}`"
        sha_cell = f" `{r.pinned_sha}` " if r.pinned_sha else " not indexed "
        status_cell = f" {clone_status_label(r)} "

        new_lines: list[str] = []
        for line in lines:
            if anchor in line and line.strip().startswith("|"):
                parts = line.split("|")
                if len(parts) >= 8:
                    parts[-3] = sha_cell
                    parts[-2] = status_cell
                    line = "|".join(parts)
            new_lines.append(line)
        lines = new_lines

    REGISTRY_PATH.write_text("\n".join(lines))


# ── Report ────────────────────────────────────────────────────────────────────


STATUS_ICON = {
    "ok": "✓",
    "already_up_to_date": "✓",
    "pulled": "↓",
    "skipped": "⚠",
    "failed": "✗",
    "not_cloned": "✗",
}

STATUS_LABEL = {
    "ok": "up to date",
    "already_up_to_date": "up to date",
    "pulled": "pulled",
    "skipped": "skipped (dirty)",
    "failed": "failed",
    "not_cloned": "not cloned",
}


def print_report(results: list[SubmoduleResult]) -> int:
    ok = sum(1 for r in results if r.sync_status in ("ok", "already_up_to_date", "pulled"))
    skipped = sum(1 for r in results if r.sync_status == "skipped")
    failed = sum(1 for r in results if r.sync_status in ("failed", "not_cloned"))

    print()
    print("AWI Submodule Sync")
    print("─" * 52)

    current_parent = None
    for r in results:
        if r.parent != current_parent:
            current_parent = r.parent
            print(f"\n  [{r.parent}]")

        icon = STATUS_ICON.get(r.sync_status, "?")
        label = STATUS_LABEL.get(r.sync_status, r.sync_status)
        indent = "    " if r.parent != "AWI" else "  "
        branch_str = f" · {r.branch}" if r.branch and r.cloned else ""
        print(f"{indent}{icon}  {r.name:<36} {label}{branch_str}")

        if r.error:
            print(f"{indent}   → {r.error}")
        for f in r.dirty_files:
            print(f"{indent}     {f}")

    print()
    print("─" * 52)
    print(f"✓ {ok} synced   ⚠ {skipped} skipped   ✗ {failed} failed")
    print()
    print("_data/submodules.md updated.")
    print()

    return 1 if (failed > 0 or skipped > 0) else 0


# ── Entry point ───────────────────────────────────────────────────────────────


def main() -> None:
    results = scan()
    results = sync_all(results)
    update_registry(results)
    exit_code = print_report(results)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
