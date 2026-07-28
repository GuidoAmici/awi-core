#!/usr/bin/env python3
"""
/awi-sync — Sync and report every repo this operator has on disk.

For each repo:
  1. Check if it is cloned locally
  2. Commit any uncommitted changes (git add -A)
  3. Checkout the tracked branch and pull
  4. Push to remote

Then the AWI root itself.

Discovery comes from the manifests, not from .gitmodules: user-submodules.json
for orgs and system repos, each org's codebases.json for its code. Nothing here
is a submodule — see ADR 0009.

Outputs a human-readable report and updates _data/submodules.md.
"""

# ── Standard library imports ──────────────────────────────────────────────────
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── Load shared path constants ────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared" / "scripts"))

from paths import AWI_ROOT, SUBMODULES_MD, USERS_RELDIR, ORGANIZATIONS_RELDIR
from manifest import plan

REGISTRY_PATH = SUBMODULES_MD

def make_node_id_factory():
    """
    Return a function that deterministically maps a submodule's last path
    segment to a unique, Mermaid-safe node id.

    Rules (stable across machines, no hand-maintained table):
      - lowercase alphanumeric slug of the segment (newhaze-api → newhazeapi)
      - leading-digit guard (42481462 → n42481462; Mermaid ids must start alpha)
      - collisions resolved with a deterministic numeric suffix (base, base2, …)
    """
    used: set = set()

    def make(segment: str) -> str:
        base = re.sub(r"[^0-9a-z]+", "", segment.lower()) or "node"
        if not base[0].isalpha():
            base = "n" + base
        node_id = base
        i = 2
        while node_id in used:
            node_id = f"{base}{i}"
            i += 1
        used.add(node_id)
        return node_id

    return make


@dataclass
class SubmoduleResult:
    name: str
    path: str
    abs_path: Path
    parent: str
    parent_abs: Path
    remote_url: str
    node_id: str
    tracked_branch: str = "main"
    cloned: bool = False
    branch: Optional[str] = None
    upstream: bool = False
    dirty: bool = False
    dirty_files: list = field(default_factory=list)
    committed: bool = False
    pushed: bool = False
    sync_status: str = "not_cloned"
    error: Optional[str] = None


# ── Git helpers ───────────────────────────────────────────────────────────────

def git(args: list, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def is_valid_git_repo(path: Path) -> bool:
    r = git(["rev-parse", "--git-dir"], cwd=path)
    return r.returncode == 0


# ── Repo discovery ────────────────────────────────────────────────────────────

def scan() -> list:
    """Build the sync list from the manifests.

    `plan()` already returns workspace repos before the codebases that live
    inside them, which is the order sync needs anyway.
    """
    make_node_id = make_node_id_factory()
    repos, warnings = plan(AWI_ROOT)

    for w in warnings:
        print(f"  ⚠ {w}", file=sys.stderr)

    results: list = []
    for repo in repos:
        parent_abs = repo.path.parent.parent if repo.is_codebase else AWI_ROOT
        results.append(SubmoduleResult(
            name=repo.name,
            path=str(repo.path.relative_to(AWI_ROOT)),
            abs_path=repo.path,
            parent=repo.parent,
            parent_abs=parent_abs,
            remote_url=repo.url,
            node_id=make_node_id(repo.name),
            tracked_branch=repo.branch,
            upstream=repo.upstream,
        ))
    return results


# ── Sync logic ────────────────────────────────────────────────────────────────

def _sync_upstream_mirror(r: SubmoduleResult, path: Path, target: str) -> SubmoduleResult:
    """Sync a read-only upstream mirror: fetch + hard-reset to origin/<target>.

    No local commit, no push — local drift is discarded so the mirror matches
    upstream exactly.
    """
    res = git(["fetch", "origin", target], cwd=path)
    if res.returncode != 0:
        r.sync_status = "failed"
        r.error = f"Fetch failed: {res.stderr.strip()}"
        return r

    if r.branch != target:
        res = git(["checkout", target], cwd=path)
        if res.returncode != 0:
            r.sync_status = "failed"
            r.error = f"Cannot checkout {target}: {res.stderr.strip()}"
            return r
        r.branch = target

    before = git(["rev-parse", "HEAD"], cwd=path).stdout.strip()
    res = git(["reset", "--hard", f"origin/{target}"], cwd=path)
    if res.returncode != 0:
        r.sync_status = "failed"
        r.error = f"Reset to origin/{target} failed: {res.stderr.strip()}"
        return r
    after = git(["rev-parse", "HEAD"], cwd=path).stdout.strip()

    # Drop untracked files too (reset --hard leaves them), so the working tree
    # matches upstream exactly and the parent gitlink isn't flagged "-dirty".
    # Gitignored build artifacts are preserved (no -x).
    git(["clean", "-fd"], cwd=path)

    r.sync_status = "pulled" if before != after else "already_up_to_date"
    return r


def sync_one(r: SubmoduleResult) -> SubmoduleResult:
    path = r.abs_path

    if not path.exists() or not (path / ".git").exists():
        r.cloned = False
        r.sync_status = "not_cloned"
        r.error = "Directory missing or not a git repo. Run: /awi-initialize"
        return r

    r.cloned = True

    if not is_valid_git_repo(path):
        r.sync_status = "failed"
        r.error = "Broken .git reference — cannot run git commands here."
        return r

    res = git(["branch", "--show-current"], cwd=path)
    r.branch = res.stdout.strip() or None
    target = r.tracked_branch

    # Upstream submodules are read-only mirrors of a third-party repo: never
    # commit local drift, never push. Just fast-forward to upstream (a hard
    # reset, so files relocated/removed upstream don't linger as fake "local
    # changes" that would later be auto-committed and cause rebase conflicts).
    if r.upstream:
        return _sync_upstream_mirror(r, path, target)

    res = git(["status", "--porcelain"], cwd=path)
    dirty_lines = [l for l in res.stdout.splitlines() if l.strip()]
    r.dirty = bool(dirty_lines)
    r.dirty_files = dirty_lines[:5]

    if r.dirty:
        git(["add", "-A"], cwd=path)
        res = git(["commit", "-m", "chore(sync): stage local changes"], cwd=path)
        if res.returncode != 0:
            nothing = "nothing to commit" in res.stdout or "nothing to commit" in res.stderr
            if nothing:
                r.dirty = False
            else:
                r.sync_status = "failed"
                r.error = f"Commit failed: {res.stderr.strip()}"
                return r
        else:
            r.committed = True

    if r.branch != target:
        res = git(["checkout", target], cwd=path)
        if res.returncode != 0:
            r.sync_status = "failed"
            r.error = f"Cannot checkout {target}: {res.stderr.strip()}"
            return r
        r.branch = target

    res = git(["pull", "--rebase", "origin", target], cwd=path)
    if res.returncode != 0:
        r.sync_status = "failed"
        r.error = f"Pull failed: {res.stderr.strip()}"
        return r

    pulled = "Already up to date" not in res.stdout

    if not r.upstream:
        res = git(["push", "origin", target], cwd=path)
        if res.returncode != 0:
            r.sync_status = "failed"
            r.error = f"Push failed: {res.stderr.strip()}"
            return r
        r.pushed = True

    r.sync_status = "pulled" if pulled else "already_up_to_date"
    return r


def sync_all(results: list) -> list:
    # Build children map: parent_name → [child results]
    children_map: dict = {}
    awi_level = []
    for r in results:
        if r.parent == "AWI":
            awi_level.append(r)
            children_map[r.name] = []
        else:
            children_map.setdefault(r.parent, []).append(r)

    # Order: for each org with children → children first, then org.
    # Orgs without children (users, upstream) go after.
    orgs_with_children = [r for r in awi_level if children_map.get(r.name)]
    orgs_without_children = [r for r in awi_level if not children_map.get(r.name)]

    ordered = []
    for org in orgs_with_children:
        ordered.extend(children_map[org.name])
        ordered.append(org)
    ordered.extend(orgs_without_children)

    synced = []
    for r in ordered:
        r = sync_one(r)
        synced.append(r)
        _write_table_row(r)
    return synced


def sync_root() -> dict:
    path = AWI_ROOT
    result: dict = {"branch": None, "committed": False, "pushed": False,
                    "status": "already_up_to_date", "error": None}

    res = git(["branch", "--show-current"], cwd=path)
    branch = res.stdout.strip()
    result["branch"] = branch

    res = git(["status", "--porcelain"], cwd=path)
    dirty = [l for l in res.stdout.splitlines() if l.strip()]
    if dirty:
        git(["add", "-A"], cwd=path)
        res = git(["commit", "-m", "chore(sync): stage local changes"], cwd=path)
        if res.returncode != 0:
            result["status"] = "failed"
            result["error"] = f"Commit failed: {res.stderr.strip()}"
            return result
        result["committed"] = True

    res = git(["pull", "--rebase", "origin", branch], cwd=path)
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


# ── Registry file creation and update ─────────────────────────────────────────

def mermaid_class(r: SubmoduleResult) -> str:
    if not r.cloned:
        return "danger"
    if r.sync_status == "failed":
        return "warning"
    return "safe"


def clone_status_label(r: SubmoduleResult) -> str:
    if not r.cloned:
        return "🔴 not cloned"
    if r.sync_status == "failed":
        return "🟡 sync failed"
    return "🟢 cloned"


def short_repo(url: str) -> str:
    """Compact a git remote URL down to `owner/repo` for readable node labels."""
    s = url.rstrip("/")
    if s.endswith(".git"):
        s = s[:-4]
    parts = s.split("/")
    return "/".join(parts[-2:]) if len(parts) >= 2 else s


def _node_box(r: SubmoduleResult) -> str:
    """Render a single Mermaid node box with name + compact repo path."""
    return f'        {r.node_id}["{r.name}<br/>{short_repo(r.remote_url)}"]'


def build_registry_file(results: list) -> None:
    awi_subs    = [r for r in results if r.parent == "AWI"]
    nested_subs = [r for r in results if r.parent != "AWI"]

    orgs  = [r for r in awi_subs if r.path.startswith(ORGANIZATIONS_RELDIR + "/")]
    users = [r for r in awi_subs if r.path.startswith(USERS_RELDIR + "/")]
    deps  = [r for r in awi_subs if r not in orgs and r not in users]

    nested_by_parent: dict = {}
    for r in nested_subs:
        nested_by_parent.setdefault(r.parent, []).append(r)

    mermaid_lines: list = [
        "```mermaid",
        "%%{init: {'flowchart': {'curve': 'linear'}}}%%",
        "graph TD",
        '    AWI(["AWI"])',
        "",
    ]

    def emit_group(label: str, members: list) -> None:
        if not members:
            return
        mermaid_lines.extend([f"    subgraph {label}", "        direction TB"])
        for r in members:
            mermaid_lines.append(_node_box(r))
        mermaid_lines.extend(["    end", ""])

    # One subgraph per org holding the org node together with its codebase
    # repos, so org → repo edges stay short instead of crossing the diagram.
    for org in orgs:
        children = nested_by_parent.get(org.name, [])
        mermaid_lines.extend(
            [f'    subgraph grp_{org.node_id}["{org.name}"]', "        direction TB"]
        )
        mermaid_lines.append(_node_box(org))
        for r in children:
            mermaid_lines.append(_node_box(r))
        if children:
            mermaid_lines.append(
                f"        {org.node_id} --> " + " & ".join(r.node_id for r in children)
            )
        mermaid_lines.extend(["    end", ""])

    # External dependencies and users get their own flat groups.
    emit_group("Dependencies", deps)
    emit_group("Users", users)

    for r in orgs + deps + users:
        mermaid_lines.append(f"    AWI --> {r.node_id}")

    all_node_ids = [r.node_id for r in results]
    mermaid_lines += [
        "",
        "    classDef safe    stroke:#a6e3a1,stroke-width:2px",
        "    classDef warning stroke:#f9e2af,stroke-width:2px",
        "    classDef danger  stroke:#f38ba8,stroke-width:2px,stroke-dasharray:4",
        "",
        f"    class {','.join(all_node_ids)} danger",
        "    linkStyle default stroke:#555,stroke-width:2px",
        "```",
    ]

    registry_lines: list = ["", "## Registry", ""]

    registry_lines += [
        "### AWI — workspace repos",
        "",
        "| Path | Local path | GitHub Repo | Type | Branch | Clone status | Last synced |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in awi_subs:
        local_path = str(r.abs_path.relative_to(AWI_ROOT))
        if r.path.startswith(USERS_RELDIR + "/"):
            repo_type = "user"
        elif r.path.startswith(ORGANIZATIONS_RELDIR + "/"):
            repo_type = "org"
        else:
            repo_type = "dependency"
        status     = clone_status_label(r)
        registry_lines.append(
            f"| `{local_path}` | `{local_path}` | {r.remote_url}"
            f" | {repo_type} |  | {status} |  |"
        )

    for parent_name, children in nested_by_parent.items():
        registry_lines += [
            "",
            f"### {parent_name} — codebases",
            "",
            "| Path | Local path | GitHub Repo | Branch | Clone status | Last synced |",
            "|---|---|---|---|---|---|",
        ]
        for r in children:
            local_path = str(r.abs_path.relative_to(AWI_ROOT))
            status     = clone_status_label(r)
            registry_lines.append(
                f"| `{r.path}` | `{local_path}` | {r.remote_url}"
                f" |  | {status} |  |"
            )

    registry_lines += [
        "",
        "### Clone status legend",
        "",
        "| Symbol | Meaning |",
        "|---|---|",
        "| 🟢 cloned · only | single-environment repo (no dev/stg pipeline) |",
        "| 🟢 cloned · dev | checked out on dev branch — codebase repo |",
        "| 🟢 cloned · prod | checked out on prod branch — stable release |",
        "| 🔴 not cloned | declared in a manifest but not on disk — **no local backup** |",
        "| Branch | value from the manifest that declares the repo |",
    ]

    content = (
        "# AWI Repo Map\n\n"
        "> Generated by /awi-sync from user-submodules.json and each org's "
        "codebases.json. Edit those, not this file.\n\n"
        + "\n".join(mermaid_lines)
        + "\n"
        + "\n".join(registry_lines)
        + "\n"
    )
    REGISTRY_PATH.write_text(content)


def _write_table_row(r: SubmoduleResult) -> None:
    if not REGISTRY_PATH.exists():
        return

    lines = REGISTRY_PATH.read_text().splitlines()
    local_path = str(r.abs_path.relative_to(AWI_ROOT))
    anchor = f"`{local_path}`"

    branch_cell = f" `{r.branch or r.tracked_branch}` "
    status_cell = f" {clone_status_label(r)} "

    synced    = r.sync_status in ("ok", "already_up_to_date", "pulled")
    sync_cell = f" {datetime.now().strftime('%Y-%m-%d %H:%M')} " if synced else None

    # Both tables end with the same three columns, so negative indices hit the
    # right cells regardless of which one the row belongs to.
    new_lines: list = []
    for line in lines:
        if anchor in line and line.strip().startswith("|"):
            parts = line.split("|")
            if len(parts) >= 8:
                parts[-4] = branch_cell
                parts[-3] = status_cell
                if sync_cell is not None:
                    parts[-2] = sync_cell
                line = "|".join(parts)
        new_lines.append(line)

    REGISTRY_PATH.write_text("\n".join(new_lines))


def update_registry(results: list, root: Optional[dict] = None) -> None:
    if not REGISTRY_PATH.exists():
        return

    lines = REGISTRY_PATH.read_text().splitlines()
    by_class: dict = {"safe": [], "warning": [], "danger": []}

    if root is not None:
        if root.get("status") == "failed":
            by_class["danger"].append("AWI")
        elif not root.get("pushed"):
            by_class["warning"].append("AWI")
        else:
            by_class["safe"].append("AWI")

    for r in results:
        by_class[mermaid_class(r)].append(r.node_id)

    new_class_lines = [
        f"    class {','.join(nodes)} {cls}"
        for cls, nodes in by_class.items()
        if nodes
    ]

    updated: list = []
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


def _count_results(results: list, root: dict) -> tuple:
    ok     = sum(1 for r in results if r.sync_status in ("ok", "already_up_to_date", "pulled"))
    failed = sum(1 for r in results if r.sync_status in ("failed", "not_cloned"))
    if root.get("status") == "failed":
        failed += 1
    return ok, failed


def print_summary(ok: int, failed: int) -> int:
    print(f"✓ {ok} synced   ✗ {failed} failed")
    return 1 if failed > 0 else 0


def print_mermaid_graph() -> None:
    if not REGISTRY_PATH.exists():
        return
    content = REGISTRY_PATH.read_text()
    start = content.find("```mermaid")
    end   = content.find("```", start + 3)
    if start != -1 and end != -1:
        print()
        print(content[start : end + 3])


def print_breakdown(results: list, root: dict) -> None:
    print()
    print("AWI Sync — Breakdown")
    print("─" * 52)

    print("\n  [AWI root]")
    icon       = STATUS_ICON.get(root["status"], "?")
    label      = STATUS_LABEL.get(root["status"], root["status"])
    branch_str = f" · {root['branch']}" if root["branch"] else ""
    tags       = (" [committed]" if root["committed"] else "") + (" [pushed]" if root["pushed"] else "")
    print(f"  {icon}  {'awi-core':<36} {label}{branch_str}{tags}")
    if root["error"]:
        print(f"     → {root['error']}")

    current_parent = None
    for r in results:
        if r.parent != current_parent:
            current_parent = r.parent
            print(f"\n  [{r.parent}]")

        icon       = STATUS_ICON.get(r.sync_status, "?")
        label      = STATUS_LABEL.get(r.sync_status, r.sync_status)
        indent     = "    " if r.parent != "AWI" else "  "
        branch_str = f" · {r.branch}" if r.branch and r.cloned else ""
        tags = (
            (" [committed]" if r.committed else "")
            + (" [upstream]" if r.upstream else (" [pushed]" if r.pushed else ""))
        )
        print(f"{indent}{icon}  {r.name:<36} {label}{branch_str}{tags}")
        if r.error:
            print(f"{indent}   → {r.error}")

    print()
    print("─" * 52)
    print()


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    breakdown = "--breakdown" in sys.argv

    results = scan()

    # Rebuild the registry structure deterministically from the manifests, so the
    # graph/table never drift when repos are added or removed. sync_all() then
    # fills per-row status; update_registry() recolors nodes.
    build_registry_file(results)

    results = sync_all(results)
    root = sync_root()
    update_registry(results, root=root)

    ok, failed = _count_results(results, root)
    exit_code  = print_summary(ok, failed)

    print_mermaid_graph()
    if breakdown or failed > 0:
        print_breakdown(results, root)

    outcome    = "completed" if exit_code == 0 else "errored"
    log_script = Path(__file__).resolve().parents[2] / "shared" / "scripts" / "log_command.py"
    subprocess.run([sys.executable, str(log_script), "awi-sync", outcome])

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
