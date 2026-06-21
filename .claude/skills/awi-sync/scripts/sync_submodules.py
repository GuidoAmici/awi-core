#!/usr/bin/env python3
"""
/awi-sync — Scan, sync, and report all AWI submodules (direct + nested).

For each submodule:
  1. Check if cloned locally
  2. Remove .gitkeep from populated folders
  3. Commit any uncommitted changes (git add -A)
  4. Checkout tracked branch and pull
  5. Push to remote

After submodules: sync AWI root itself, then mirror drift to awi-core upstream branch.

Outputs a human-readable report and updates _data/submodules.md.
"""

# ── Standard library imports ──────────────────────────────────────────────────
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── Load shared path constants ────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared" / "scripts"))

from paths import AWI_ROOT, SUBMODULES_MD, USERS_RELDIR, ORGANIZATIONS_RELDIR, CURRENT_USER
from sync_status import collect_core_files, collect_instance_files, md5

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
    pinned_sha: Optional[str] = None
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


def get_pinned_sha(repo_root: Path, submodule_path: str) -> Optional[str]:
    r = git(["ls-files", "--stage", "--", submodule_path], cwd=repo_root)
    for line in r.stdout.splitlines():
        if line.startswith("160000"):
            return line.split()[1][:8]
    return None


def is_valid_git_repo(path: Path) -> bool:
    r = git(["rev-parse", "--git-dir"], cwd=path)
    return r.returncode == 0


# ── User config helpers ───────────────────────────────────────────────────────

def read_user_config() -> dict:
    """
    Read user-config.json from the current user's directory.
    Returns an empty dict if current-user.json or user-config.json is missing.

    Schema documented at:
      _system/_agentic-workflow-integrator/references/user-config-schema.md
    """
    if not CURRENT_USER.exists():
        return {}
    try:
        current = json.loads(CURRENT_USER.read_text())
        user_path = current.get("user", "")
        config_path = AWI_ROOT / user_path / "user-config.json"
        if config_path.exists():
            return json.loads(config_path.read_text())
    except (json.JSONDecodeError, OSError, KeyError):
        pass
    return {}


def check_awi_core_write_permission(core_root: Path) -> bool:
    """
    Use gh api to verify the authenticated user has push access to awi-core.
    Returns True if write permission is confirmed, False otherwise.
    """
    res = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=core_root,
        capture_output=True,
        text=True,
    )
    remote_url = res.stdout.strip()
    if "github.com" in remote_url:
        repo_slug = remote_url.split("github.com")[-1].lstrip(":/").rstrip(".git")
    else:
        return False

    res = subprocess.run(
        ["gh", "api", f"repos/{repo_slug}", "--jq", ".permissions.push"],
        capture_output=True,
        text=True,
    )
    return res.returncode == 0 and res.stdout.strip() == "true"


# ── Submodule discovery ───────────────────────────────────────────────────────

def parse_gitmodules(path: Path) -> list:
    if not path.exists():
        return []
    modules: list = []
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


def scan() -> list:
    results: list = []
    make_node_id = make_node_id_factory()

    awi_modules = parse_gitmodules(AWI_ROOT / ".gitmodules")
    for m in awi_modules:
        sub_path = m.get("path", m["name"])
        abs_path = AWI_ROOT / sub_path
        name = sub_path.split("/")[-1]
        node_id = make_node_id(name)
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

    for parent in list(results):
        nested_path = parent.abs_path / ".gitmodules"
        if not nested_path.exists():
            continue
        for m in parse_gitmodules(nested_path):
            sub_path = m.get("path", m["name"])
            abs_path = parent.abs_path / sub_path
            name = sub_path.split("/")[-1]
            node_id = make_node_id(name)
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

    r.sync_status = "pulled" if before != after else "already_up_to_date"
    return r


def sync_one(r: SubmoduleResult) -> SubmoduleResult:
    path = r.abs_path

    if not path.exists() or not (path / ".git").exists():
        r.cloned = False
        r.sync_status = "not_cloned"
        r.error = "Directory missing or not a git repo. Run: git submodule update --init"
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
        res = git(["commit", "-m", "cos: sync - stage local changes"], cwd=path)
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
        res = git(["commit", "-m", "cos: sync - stage local changes"], cwd=path)
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


def find_awi_core_path(awi_root: Path) -> Optional[Path]:
    for gitmodules in sorted(awi_root.rglob(".gitmodules")):
        if ".git" in gitmodules.parts:
            continue
        current_path = None
        for line in gitmodules.read_text().splitlines():
            line = line.strip()
            if line.startswith("path ="):
                current_path = line.split("=", 1)[1].strip()
            elif line.startswith("url =") and "GuidoAmici/awi-core" in line:
                if current_path:
                    return gitmodules.parent / current_path
    return None


def mirror_instance_to_awi_core() -> dict:
    """
    Mirror AWI instance source files to the awi-core upstream branch.

    Three-state collaborator push logic driven by user-config.json:
      - collaborator absent or false  → skip silently (status: "skipped")
      - collaborator true, no gh perm → warning (status: "no_permission")
      - collaborator true, push fails → error (status: "failed")

    The upstream branch is read from user-config.awi_upstream_branch
    (defaults to "dev" if absent).
    """
    result: dict = {"drift": [], "missing": [], "committed": False,
                    "pushed": False, "status": "ok", "error": None}

    # ── Collaborator gate ──────────────────────────────────────────────────────
    user_config = read_user_config()
    is_collaborator = user_config.get("collaborator", False)

    if not is_collaborator:
        result["status"] = "skipped"
        return result

    # ── Find awi-core on disk ──────────────────────────────────────────────────
    core_root = find_awi_core_path(AWI_ROOT)

    if not core_root or not core_root.is_dir():
        result["status"] = "failed"
        result["error"] = "awi-core not found — no submodule with url GuidoAmici/awi-core in .gitmodules"
        return result

    # ── Verify write permission via gh api ────────────────────────────────────
    has_permission = check_awi_core_write_permission(core_root)
    if not has_permission:
        result["status"] = "no_permission"
        result["error"] = "Warning: collaborator flag is set but awi-core write access could not be confirmed"
        return result

    # ── Determine upstream branch from user config ────────────────────────────
    upstream_branch = user_config.get("awi_upstream_branch", "dev")

    res = git(["checkout", upstream_branch], cwd=core_root)
    if res.returncode != 0:
        result["status"] = "failed"
        result["error"] = f"Cannot checkout {upstream_branch}: {res.stderr.strip()}"
        return result

    local_files = collect_instance_files(AWI_ROOT)
    core_files = collect_core_files(core_root)

    for rel, local_path in sorted(local_files.items()):
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

    res = git(["push", "origin", upstream_branch], cwd=core_root)
    if res.returncode != 0:
        result["status"] = "failed"
        result["error"] = f"Error: push to awi-core failed: {res.stderr.strip()}"
        return result
    result["pushed"] = True
    result["status"] = "synced"

    return result


def pull_from_awi_core() -> dict:
    """
    Copy awi-core source files into the AWI instance.

    Runs after sync_all() so the awi-core submodule is already up to date.
    No collaborator gate — all users run this.

    Uses the same file set as mirror_instance_to_awi_core() but in reverse:
    collect_core_files() → copy to instance paths.
    """
    result: dict = {"updated": [], "added": [], "status": "ok", "error": None}

    core_root = find_awi_core_path(AWI_ROOT)
    if not core_root or not core_root.is_dir():
        result["status"] = "failed"
        result["error"] = "awi-core not found — no submodule with url GuidoAmici/awi-core in .gitmodules"
        return result

    core_files = collect_core_files(core_root)
    instance_files = collect_instance_files(AWI_ROOT)

    for rel, core_path in sorted(core_files.items()):
        dest = AWI_ROOT / rel
        if rel in instance_files:
            if md5(core_path) != md5(instance_files[rel]):
                shutil.copy2(core_path, dest)
                result["updated"].append(rel)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(core_path, dest)
            result["added"].append(rel)

    if result["updated"] or result["added"]:
        result["status"] = "synced"

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
        "### AWI — direct submodules",
        "",
        "| Path | Local path | GitHub Repo | Type | Branch | SHA | Clone status | Last synced |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in awi_subs:
        local_path = str(r.abs_path.relative_to(AWI_ROOT))
        if r.path.startswith(USERS_RELDIR + "/"):
            repo_type = "user"
        elif r.path.startswith(ORGANIZATIONS_RELDIR + "/"):
            repo_type = "org"
        else:
            repo_type = "dependency"
        sha_cell   = f"`{r.pinned_sha}`" if r.pinned_sha else "not indexed"
        status     = clone_status_label(r)
        registry_lines.append(
            f"| `{local_path}` | `{local_path}` | {r.remote_url}"
            f" | {repo_type} |  |  | {status} |  |"
        )

    for parent_name, children in nested_by_parent.items():
        registry_lines += [
            "",
            f"### {parent_name} — codebase submodules",
            "",
            "| Path | Local path | GitHub Repo | Branch | SHA | Clone status | Last synced |",
            "|---|---|---|---|---|---|---|",
        ]
        for r in children:
            local_path = str(r.abs_path.relative_to(AWI_ROOT))
            status     = clone_status_label(r)
            registry_lines.append(
                f"| `{r.path}` | `{local_path}` | {r.remote_url}"
                f" |  |  | {status} |  |"
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
        "| 🔴 not cloned | registered but directory empty — **no local backup** |",
        "| Branch | value from `.gitmodules branch =` (used by `git submodule update --remote`) |",
    ]

    content = (
        "# AWI Submodule Map\n\n"
        "> Update this diagram and registry whenever submodules are added, removed, or restructured.\n\n"
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
    sha_cell    = f" `{r.pinned_sha}` " if r.pinned_sha else " not indexed "
    status_cell = f" {clone_status_label(r)} "

    synced    = r.sync_status in ("ok", "already_up_to_date", "pulled")
    sync_cell = f" {datetime.now().strftime('%Y-%m-%d %H:%M')} " if synced else None

    new_lines: list = []
    for line in lines:
        if anchor in line and line.strip().startswith("|"):
            parts = line.split("|")
            if len(parts) >= 8:
                parts[-5] = branch_cell
                parts[-4] = sha_cell
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


def _count_results(results: list, root: dict, mirror: dict, pull: dict) -> tuple:
    ok     = sum(1 for r in results if r.sync_status in ("ok", "already_up_to_date", "pulled"))
    failed = sum(1 for r in results if r.sync_status in ("failed", "not_cloned"))
    if root.get("status") == "failed":
        failed += 1
    # "skipped" and "no_permission" are not counted as failures
    if mirror.get("status") == "failed":
        failed += 1
    if pull.get("status") == "failed":
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


def print_breakdown(results: list, root: dict, mirror: dict, pull: dict) -> None:
    print()
    print("AWI Submodule Sync — Breakdown")
    print("─" * 52)

    print("\n  [AWI root]")
    icon       = STATUS_ICON.get(root["status"], "?")
    label      = STATUS_LABEL.get(root["status"], root["status"])
    branch_str = f" · {root['branch']}" if root["branch"] else ""
    tags       = (" [committed]" if root["committed"] else "") + (" [pushed]" if root["pushed"] else "")
    print(f"  {icon}  {'my-awi-instance':<36} {label}{branch_str}{tags}")
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

    # awi-core mirror (instance → awi-core) — collaborator only
    print("\n  [awi-core mirror ↑]")
    if mirror["status"] == "skipped":
        pass  # Non-collaborator: silent skip
    elif mirror["status"] == "no_permission":
        print(f"  ⚠  {'awi-core':<36} {mirror['error']}")
    elif mirror["status"] == "ok":
        print(f"  ✓  {'awi-core':<36} up to date")
    elif mirror["status"] == "synced":
        n_drift   = len(mirror["drift"])
        n_missing = len(mirror["missing"])
        tags = (" [committed]" if mirror["committed"] else "") + (" [pushed]" if mirror["pushed"] else "")
        print(f"  ↑  {'awi-core':<36} {n_drift} drift, {n_missing} missing pushed{tags}")
    elif mirror["status"] == "failed":
        print(f"  ✗  {'awi-core':<36} {mirror['error']}")

    # awi-core pull (awi-core → instance) — all users
    print("\n  [awi-core pull ↓]")
    if pull["status"] == "ok":
        print(f"  ✓  {'awi-core':<36} up to date")
    elif pull["status"] == "synced":
        n_updated = len(pull["updated"])
        n_added   = len(pull["added"])
        print(f"  ↓  {'awi-core':<36} {n_updated} updated, {n_added} added")
    elif pull["status"] == "failed":
        print(f"  ✗  {'awi-core':<36} {pull['error']}")

    print()
    print("─" * 52)
    print()


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    breakdown = "--breakdown" in sys.argv

    results = scan()

    # Always rebuild the registry structure deterministically from .gitmodules,
    # so the graph/table never drift when submodules are added or removed.
    # sync_all() then fills per-row status; update_registry() recolors nodes.
    build_registry_file(results)

    # 1. Mirror instance → awi-core (collaborators only, must run before sync_all
    #    so changes are in awi-core remote before the submodule pull merges them)
    mirror = mirror_instance_to_awi_core()
    if mirror["status"] == "no_permission":
        print(mirror["error"], file=sys.stderr)
    elif mirror["status"] == "failed" and mirror.get("error"):
        print(mirror["error"], file=sys.stderr)

    # 2. Sync all submodules (includes git pull on awi-core submodule)
    results = sync_all(results)
    root = sync_root()
    update_registry(results, root=root)

    # 3. Pull awi-core → instance (all users, runs after awi-core submodule is up to date)
    pull = pull_from_awi_core()
    if pull["status"] == "failed" and pull.get("error"):
        print(pull["error"], file=sys.stderr)

    ok, failed = _count_results(results, root, mirror, pull)
    exit_code  = print_summary(ok, failed)

    print_mermaid_graph()
    if breakdown or failed > 0:
        print_breakdown(results, root, mirror, pull)

    outcome    = "completed" if exit_code == 0 else "errored"
    log_script = Path(__file__).resolve().parents[2] / "shared" / "scripts" / "log_command.py"
    subprocess.run([sys.executable, str(log_script), "awi-sync", outcome])

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
