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

# ── Standard library imports ──────────────────────────────────────────────────
# These come with Python — no installation needed.

import shutil        # File copy operations (used when mirroring to awi-core)
import subprocess    # Runs shell commands (git) as child processes
import sys           # Used to exit with a status code at the end
from dataclasses import dataclass, field   # Lets us define structs (SubmoduleResult)
from datetime import datetime              # Used to timestamp "Last synced" cells
from pathlib import Path                   # Cross-platform file path handling
from typing import Optional                # Lets us say "this value might be None"

# ── Load shared path constants ────────────────────────────────────────────────
# Adds the shared/scripts folder to the Python search path so we can import
# from it, even though it's outside this script's own directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared" / "scripts"))

from paths import AWI_ROOT, SUBMODULES_MD, USERS_RELDIR
# AWI_ROOT     — absolute path to the root of the AWI repo on disk
# SUBMODULES_MD — absolute path to _data/submodules.md
# USERS_RELDIR  — relative path prefix for user submodules (e.g. "_data/users")

from sync_status import collect_core_files, collect_instance_files, md5
# Used later when mirroring files to awi-core

# ── Registry file path ────────────────────────────────────────────────────────
# An alias so the code reads clearly: "REGISTRY_PATH" is the file we update.
REGISTRY_PATH = SUBMODULES_MD

# ── Mermaid node ID map for nested repos ─────────────────────────────────────
# Mermaid diagrams need short IDs for each node (no spaces, no slashes).
# AWI-level entries are built automatically from .gitmodules.
# Nested repos (inside a client) must be listed here manually.
# Key: (parent_name, relative_path_in_parent)  →  Value: short node ID
_NESTED_NODE_IDS: dict[tuple[str, str], str] = {
    ("newhaze", "codebase/newhaze-api"): "api",
    ("newhaze", "codebase/newhaze-b2b-panel"): "b2b",
    ("newhaze", "codebase/newhaze-consumer-panel"): "consumer",
    ("newhaze", "codebase/newhaze-intern-panel"): "intern",
    ("newhaze", "codebase/newhaze-learn"): "learn",
    ("newhaze", "codebase/newhaze-ui"): "ui",
    ("newhaze", "codebase/newhaze-website"): "website",
    ("newhaze", "documentation/wiki"): "wiki",
    ("rabbitek", "codebase/awi-core"): "awicore",
}


def build_node_id_map() -> dict[tuple[str, str], str]:
    """
    Build the complete node ID map by combining:
    - AWI-level entries derived from .gitmodules (auto-generated)
    - Nested entries from _NESTED_NODE_IDS (manually configured above)

    Returns a dict mapping (parent, path) → short Mermaid node ID.
    Falls back to the folder basename if a path isn't in the map.
    """
    mapping: dict[tuple[str, str], str] = {}

    # For each AWI-level submodule, derive a short ID:
    # - user submodules → always "user"
    # - others → last segment of the path, with hyphens removed
    for m in parse_gitmodules(AWI_ROOT / ".gitmodules"):
        path = m.get("path", m["name"])
        if path.startswith(USERS_RELDIR + "/"):
            node_id = "user"
        else:
            node_id = path.split("/")[-1].replace("-", "")
        mapping[("AWI", path)] = node_id

    # Merge in the manually-defined nested node IDs
    mapping.update(_NESTED_NODE_IDS)
    return mapping


# ── Data model ────────────────────────────────────────────────────────────────
# SubmoduleResult is a struct that holds everything we know about one submodule.
# We populate it during scan(), then update it during sync_one().

@dataclass
class SubmoduleResult:
    name: str                   # Folder name, e.g. "newhaze"
    path: str                   # Path relative to its parent repo, e.g. "_data/clients/newhaze"
    abs_path: Path              # Full path on disk
    parent: str                 # "AWI" for top-level, or parent submodule name for nested
    parent_abs: Path            # Full path of the parent repo root on disk
    remote_url: str             # GitHub URL / identifier from .gitmodules
    node_id: str                # Short ID used in Mermaid diagram
    tracked_branch: str = "main"         # Branch this submodule should stay on
    cloned: bool = False                 # True if the folder exists and is a git repo
    branch: Optional[str] = None        # Currently checked-out branch (None = detached HEAD)
    pinned_sha: Optional[str] = None    # SHA the parent repo has pinned for this submodule
    upstream: bool = False              # True = read-only upstream; skip pushing
    dirty: bool = False                 # True if there were uncommitted changes
    dirty_files: list = field(default_factory=list)  # First 5 dirty file paths (for display)
    committed: bool = False             # True if we committed dirty files
    pushed: bool = False                # True if we successfully pushed
    # Possible values: ok | already_up_to_date | pulled | failed | not_cloned
    sync_status: str = "not_cloned"
    error: Optional[str] = None         # Human-readable error message if something went wrong


# ── Git helpers ───────────────────────────────────────────────────────────────

def git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """
    Run a git command in the given directory and return the result.
    The result has .returncode (0 = success), .stdout, and .stderr.
    capture_output=True means we capture stdout/stderr instead of printing them.
    """
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def get_pinned_sha(repo_root: Path, submodule_path: str) -> Optional[str]:
    """
    Return the 8-character SHA that the parent repo has 'pinned' for this
    submodule. Git stores the exact commit a submodule points to; this reads it.
    Returns None if the submodule isn't staged/tracked yet.
    """
    r = git(["ls-files", "--stage", "--", submodule_path], cwd=repo_root)
    for line in r.stdout.splitlines():
        if line.startswith("160000"):   # 160000 is the git mode for a submodule
            return line.split()[1][:8]  # Return first 8 chars of the SHA
    return None


def is_valid_git_repo(path: Path) -> bool:
    """Return True if the given path is a valid git repository."""
    r = git(["rev-parse", "--git-dir"], cwd=path)
    return r.returncode == 0


def in_nested_repo(file_path: Path, repo_root: Path) -> bool:
    """
    Return True if file_path is inside a nested git repo (i.e. a submodule).
    We walk up the directory tree looking for a .git folder, stopping at repo_root.
    This prevents us from touching files that belong to a different git repo.
    """
    p = file_path.parent
    while p != repo_root:
        if (p / ".git").exists():
            return True
        p = p.parent
    return False


def clean_gitkeeps(repo_root: Path) -> None:
    """
    Maintain .gitkeep placeholder files:
    - Remove .gitkeep from folders that now have real content
    - Create .gitkeep in folders that are empty (so git tracks them)
    Skips folders that belong to nested git repos (submodules).
    """
    for dirpath in repo_root.rglob("*"):
        if not dirpath.is_dir():
            continue
        if in_nested_repo(dirpath, repo_root):
            continue
        contents = list(dirpath.iterdir())
        non_gitkeep = [f for f in contents if f.name != ".gitkeep"]
        gitkeep = dirpath / ".gitkeep"
        if non_gitkeep:
            # Folder has real files — remove the placeholder
            if gitkeep.exists():
                gitkeep.unlink()
        else:
            # Folder is empty — ensure placeholder exists
            if not gitkeep.exists():
                gitkeep.touch()


# ── Submodule discovery ───────────────────────────────────────────────────────

def parse_gitmodules(path: Path) -> list[dict]:
    """
    Parse a .gitmodules file and return a list of dicts, one per submodule.
    Each dict has keys like "name", "path", "url", "branch", "upstream".
    Returns an empty list if the file doesn't exist.
    """
    if not path.exists():
        return []
    modules: list[dict] = []
    current: dict = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[submodule"):
            # Start of a new submodule block — save the previous one
            if current:
                modules.append(current)
            current = {"name": line.split('"')[1]}  # Extract name from [submodule "name"]
        elif "=" in line and current is not None:
            # A key = value line inside a submodule block
            key, _, val = line.partition("=")
            current[key.strip()] = val.strip()
    if current:
        modules.append(current)
    return modules


def scan() -> list[SubmoduleResult]:
    """
    Discover all submodules registered in AWI:
    1. Read AWI root's .gitmodules for direct submodules
    2. For each cloned client, read their .gitmodules for nested repos
    Returns a list of SubmoduleResult (not yet synced — just discovered).
    """
    results: list[SubmoduleResult] = []
    node_id_map = build_node_id_map()

    # Step 1 — AWI direct submodules (top-level entries in AWI's .gitmodules)
    awi_modules = parse_gitmodules(AWI_ROOT / ".gitmodules")
    for m in awi_modules:
        sub_path = m.get("path", m["name"])
        abs_path = AWI_ROOT / sub_path
        name = sub_path.split("/")[-1]   # Just the folder name, not the full path
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

    # Step 2 — Nested submodules (repos inside each client submodule)
    # We only find these if the client folder exists and has its own .gitmodules
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
    """
    Sync a single submodule: commit local changes, pull, push.
    Updates r.sync_status and r.error in place and returns r.
    """
    path = r.abs_path

    # If the directory doesn't exist or has no .git folder, it's not cloned
    if not path.exists() or not (path / ".git").exists():
        r.cloned = False
        r.sync_status = "not_cloned"
        r.error = "Directory missing or not a git repo. Run: git submodule update --init"
        return r

    r.cloned = True

    # Extra safety check — the .git folder exists but might be broken
    if not is_valid_git_repo(path):
        r.sync_status = "failed"
        r.error = "Broken .git reference — cannot run git commands here."
        return r

    # Get the currently checked-out branch name
    res = git(["branch", "--show-current"], cwd=path)
    r.branch = res.stdout.strip() or None   # Empty string means detached HEAD

    # Check for uncommitted changes — if any, commit them all
    res = git(["status", "--porcelain"], cwd=path)
    dirty_lines = [l for l in res.stdout.splitlines() if l.strip()]
    r.dirty = bool(dirty_lines)
    r.dirty_files = dirty_lines[:5]   # Store first 5 for display

    if r.dirty:
        git(["add", "-A"], cwd=path)
        res = git(["commit", "-m", "cos: sync - stage local changes"], cwd=path)
        if res.returncode != 0:
            r.sync_status = "failed"
            r.error = f"Commit failed: {res.stderr.strip()}"
            return r
        r.committed = True

    # Switch to the tracked branch if we're on a different one
    target = r.tracked_branch
    if r.branch != target:
        res = git(["checkout", target], cwd=path)
        if res.returncode != 0:
            r.sync_status = "failed"
            r.error = f"Cannot checkout {target}: {res.stderr.strip()}"
            return r
        r.branch = target

    # Pull latest changes from the remote (rebase to avoid divergent branch errors)
    res = git(["pull", "--rebase", "origin", target], cwd=path)
    if res.returncode != 0:
        r.sync_status = "failed"
        r.error = f"Pull failed: {res.stderr.strip()}"
        return r

    pulled = "Already up to date" not in res.stdout

    # Push our local commits upstream (skip for read-only upstream repos)
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
    """
    Sync every submodule in the list one by one.
    After each sync, immediately update that submodule's row in the registry file.
    Returns the updated list.
    """
    synced = []
    for r in results:
        r = sync_one(r)
        synced.append(r)
        _write_table_row(r)   # Update the registry file row right away
    return synced


def sync_root() -> dict:
    """
    Sync the AWI root repo itself (commit + pull + push on the current branch).
    This runs after submodules so any updated submodule pointers are included.
    Returns a dict with keys: branch, committed, pushed, status, error.
    """
    path = AWI_ROOT
    result: dict = {"branch": None, "committed": False, "pushed": False,
                    "status": "already_up_to_date", "error": None}

    res = git(["branch", "--show-current"], cwd=path)
    branch = res.stdout.strip()
    result["branch"] = branch

    # Commit any local changes (e.g. updated submodule pointers)
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
    """
    Scan all .gitmodules files under awi_root to find the local path of awi-core.
    We search by the GitHub URL rather than by name, so renames don't break things.
    Returns the absolute path to awi-core, or None if not found.
    """
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


def sync_awi_core() -> dict:
    """
    Mirror AWI instance source files to the awi-core dev-claude branch.
    This keeps the shared template repo in sync with any local customizations.
    Returns a dict with keys: drift, missing, committed, pushed, status, error.
    """
    result: dict = {"drift": [], "missing": [], "committed": False,
                    "pushed": False, "status": "ok", "error": None}

    core_root = find_awi_core_path(AWI_ROOT)

    if not core_root or not core_root.is_dir():
        result["status"] = "failed"
        result["error"] = "awi-core not found — no submodule with url GuidoAmici/awi-core in .gitmodules"
        return result

    res = git(["checkout", "dev-claude"], cwd=core_root)
    if res.returncode != 0:
        result["status"] = "failed"
        result["error"] = f"Cannot checkout dev-claude: {res.stderr.strip()}"
        return result

    local_files = collect_instance_files(AWI_ROOT)
    core_files = collect_core_files(core_root)

    # Compare files: copy any that are missing in core or have different content
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

    # Nothing changed — no commit needed
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


# ── Registry file creation and update ─────────────────────────────────────────

def mermaid_class(r: SubmoduleResult) -> str:
    """
    Return the Mermaid CSS class name for a submodule node based on its status.
    "safe" = green border, "warning" = yellow, "danger" = red dashed.
    """
    if not r.cloned:
        return "danger"
    if r.sync_status == "failed":
        return "warning"
    return "safe"


def clone_status_label(r: SubmoduleResult) -> str:
    """Return the emoji + text label shown in the Clone status column."""
    if not r.cloned:
        return "🔴 not cloned"
    if r.sync_status == "failed":
        return "🟡 sync failed"
    return "🟢 cloned"


def create_registry_file(results: list[SubmoduleResult]) -> None:
    """
    Create _data/submodules.md from scratch when the file doesn't exist.

    The file has two sections:
    1. A Mermaid diagram — a visual map of the submodule tree
    2. Registry tables — one table per group (AWI direct + each nested parent)

    Table column layout (must match what _write_table_row() expects):
      AWI table    (8 cols): Path | Local path | GitHub Repo | Type | Branch | SHA | Clone status | Last synced
      Nested table (7 cols): Path | Local path | GitHub Repo | Branch | SHA | Clone status | Last synced

    _write_table_row() updates the last 4 data columns using negative indices:
      parts[-5] → Branch, parts[-4] → SHA, parts[-3] → Clone status, parts[-2] → Last synced
    """

    # Separate AWI-level submodules from nested ones
    awi_subs    = [r for r in results if r.parent == "AWI"]
    nested_subs = [r for r in results if r.parent != "AWI"]

    # Split AWI submodules into clients (codebase repos) and users
    clients = [r for r in awi_subs if not r.path.startswith(USERS_RELDIR + "/")]
    users   = [r for r in awi_subs if r.path.startswith(USERS_RELDIR + "/")]

    # Group nested submodules by their parent name, preserving insertion order
    nested_by_parent: dict[str, list[SubmoduleResult]] = {}
    for r in nested_subs:
        nested_by_parent.setdefault(r.parent, []).append(r)

    # ── Build the Mermaid diagram ──────────────────────────────────────────
    # Each subgraph groups related repos visually. Edges show parent → child.

    mermaid_lines: list[str] = [
        "```mermaid",
        "graph TD",
        "    AWI",
        "",
    ]

    # Clients subgraph — one node per client submodule
    if clients:
        mermaid_lines += ["    subgraph Clients", "        direction TD"]
        for r in clients:
            mermaid_lines.append(f'        {r.node_id}["{r.name}\\n{r.remote_url}"]')
        mermaid_lines += ["    end", ""]

    # Users subgraph
    if users:
        mermaid_lines += ["    subgraph Users", "        direction TD"]
        for r in users:
            mermaid_lines.append(f'        {r.node_id}["{r.name}\\n{r.remote_url}"]')
        mermaid_lines += ["    end", ""]

    # One subgraph per client that has nested repos (e.g. "NewHaze repos")
    for parent_name, children in nested_by_parent.items():
        label = f"{parent_name.capitalize()} repos"
        mermaid_lines += [f"    subgraph {label}", "        direction TD"]
        for r in children:
            mermaid_lines.append(f'        {r.node_id}["{r.name}\\n{r.remote_url}"]')
        mermaid_lines += ["    end", ""]

    # Edges: AWI → clients and AWI → users
    if clients:
        mermaid_lines.append("    AWI --> " + " & ".join(r.node_id for r in clients))
    if users:
        mermaid_lines.append("    AWI --> " + " & ".join(r.node_id for r in users))

    # Edges: each parent client → its nested children
    for parent_name, children in nested_by_parent.items():
        parent_node = next((r.node_id for r in awi_subs if r.name == parent_name), parent_name)
        mermaid_lines.append(f"    {parent_node} --> " + " & ".join(r.node_id for r in children))

    # Style definitions and initial class assignments (all danger = not yet synced)
    all_node_ids = [r.node_id for r in results]
    mermaid_lines += [
        "",
        "    classDef safe    stroke:#a6e3a1,stroke-width:2px",
        "    classDef warning stroke:#f9e2af,stroke-width:2px",
        "    classDef danger  stroke:#f38ba8,stroke-width:2px,stroke-dasharray:4",
        "",
        f"    class {','.join(all_node_ids)} danger",
        "```",
    ]

    # ── Build registry tables ──────────────────────────────────────────────
    # One table for AWI direct submodules, then one per nested parent.

    registry_lines: list[str] = ["", "## Registry", ""]

    # AWI direct submodules — 8-column table
    registry_lines += [
        "### AWI — direct submodules",
        "",
        "| Path | Local path | GitHub Repo | Type | Branch | SHA | Clone status | Last synced |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in awi_subs:
        local_path = str(r.abs_path.relative_to(AWI_ROOT))
        repo_type  = "user" if r.path.startswith(USERS_RELDIR + "/") else "client"
        sha_cell   = f"`{r.pinned_sha}`" if r.pinned_sha else "not indexed"
        status     = clone_status_label(r)
        registry_lines.append(
            f"| `{local_path}` | `{local_path}` | {r.remote_url}"
            f" | {repo_type} |  |  | {status} |  |"
        )

    # Nested submodule tables — 7-column table (no Type column)
    for parent_name, children in nested_by_parent.items():
        registry_lines += [
            "",
            f"### {parent_name}-client — nested submodules",
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

    # Clone status legend
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

    # ── Write the file ─────────────────────────────────────────────────────
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
    """
    Update one row in the registry table for submodule r.
    Finds the row by looking for the submodule's local path as an anchor.
    Updates the last 4 data columns: Branch, SHA, Clone status, Last synced.

    Column layout (negative indices from the right):
      parts[-5] = Branch, parts[-4] = SHA, parts[-3] = Clone status, parts[-2] = Last synced
    This works because markdown table rows split by "|" give:
      ['', col1, col2, ..., colN, '']  — the last element is always an empty string.
    """
    if not REGISTRY_PATH.exists():
        return   # Safety check — should not happen after create_registry_file()

    lines = REGISTRY_PATH.read_text().splitlines()
    local_path = str(r.abs_path.relative_to(AWI_ROOT))
    anchor = f"`{local_path}`"           # We search for this exact string in each line

    branch_cell = f" `{r.branch or r.tracked_branch}` "
    sha_cell    = f" `{r.pinned_sha}` " if r.pinned_sha else " not indexed "
    status_cell = f" {clone_status_label(r)} "

    # Only write a "Last synced" timestamp if the sync actually succeeded
    synced     = r.sync_status in ("ok", "already_up_to_date", "pulled")
    sync_cell  = f" {datetime.now().strftime('%Y-%m-%d %H:%M')} " if synced else None

    new_lines: list[str] = []
    for line in lines:
        # Only process table rows that contain the anchor for this submodule
        if anchor in line and line.strip().startswith("|"):
            parts = line.split("|")
            # Require at least 8 parts (= 6 data columns minimum)
            if len(parts) >= 8:
                parts[-5] = branch_cell
                parts[-4] = sha_cell
                parts[-3] = status_cell
                if sync_cell is not None:
                    parts[-2] = sync_cell
                line = "|".join(parts)
        new_lines.append(line)

    REGISTRY_PATH.write_text("\n".join(new_lines))


def update_registry(results: list[SubmoduleResult], root: Optional[dict] = None) -> None:
    """
    Rebuild the Mermaid `class` lines in the diagram based on final sync results.
    Called once after all submodules have been synced.
    Replaces all existing `class X safe/warning/danger` lines with new ones.
    """
    if not REGISTRY_PATH.exists():
        return   # Safety check

    lines = REGISTRY_PATH.read_text().splitlines()

    # Group node IDs by their visual class (color)
    by_class: dict[str, list[str]] = {"safe": [], "warning": [], "danger": []}

    # The AWI root node itself (the repo, not a submodule)
    if root is not None:
        if root.get("status") == "failed":
            by_class["danger"].append("AWI")
        elif not root.get("pushed"):
            by_class["warning"].append("AWI")
        else:
            by_class["safe"].append("AWI")

    # All individual submodules
    for r in results:
        by_class[mermaid_class(r)].append(r.node_id)

    # Build replacement class lines, skipping empty classes
    new_class_lines = [
        f"    class {','.join(nodes)} {cls}"
        for cls, nodes in by_class.items()
        if nodes
    ]

    # Replace all existing class lines with the new ones (insert once, skip duplicates)
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
            # Existing class line is dropped — replaced by new_class_lines above
        else:
            updated.append(line)

    REGISTRY_PATH.write_text("\n".join(updated))


# ── Report ────────────────────────────────────────────────────────────────────

# Maps internal status codes to the symbols printed in the --breakdown output
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


def _count_results(
    results: list[SubmoduleResult], root: dict, core: dict
) -> tuple[int, int]:
    """
    Count synced vs failed across submodules, AWI root, and awi-core.
    Returns (ok, failed).
    """
    ok     = sum(1 for r in results if r.sync_status in ("ok", "already_up_to_date", "pulled"))
    failed = sum(1 for r in results if r.sync_status in ("failed", "not_cloned"))
    if root.get("status") == "failed":
        failed += 1
    if core.get("status") == "failed":
        failed += 1
    return ok, failed


def print_summary(ok: int, failed: int) -> int:
    """
    Always-printed 1-line summary.
    Returns exit code: 0 if everything succeeded, 1 if anything failed.
    """
    print(f"✓ {ok} synced   ✗ {failed} failed")
    return 1 if failed > 0 else 0


def print_mermaid_graph() -> None:
    """
    Read _data/submodules.md and print the Mermaid diagram block to stdout.
    Printed when --full-report is passed.
    """
    if not REGISTRY_PATH.exists():
        return
    content = REGISTRY_PATH.read_text()
    # Find the opening ```mermaid fence and its closing ``` fence
    start = content.find("```mermaid")
    end   = content.find("```", start + 3)
    if start != -1 and end != -1:
        print()
        print(content[start : end + 3])


def print_breakdown(
    results: list[SubmoduleResult], root: dict, core: dict
) -> None:
    """
    Per-submodule text breakdown — printed when --breakdown is passed.
    Shows each repo's sync status, branch, commit/push tags, and any errors.
    """
    print()
    print("AWI Submodule Sync — Breakdown")
    print("─" * 52)

    # AWI root repo status
    print("\n  [AWI root]")
    icon       = STATUS_ICON.get(root["status"], "?")
    label      = STATUS_LABEL.get(root["status"], root["status"])
    branch_str = f" · {root['branch']}" if root["branch"] else ""
    tags       = (" [committed]" if root["committed"] else "") + (" [pushed]" if root["pushed"] else "")
    print(f"  {icon}  {'my-awi-instance':<36} {label}{branch_str}{tags}")
    if root["error"]:
        print(f"     → {root['error']}")

    # Each submodule — grouped by parent for readability
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

    # awi-core mirror status
    print("\n  [awi-core → dev-claude]")
    if core["status"] == "ok":
        print(f"  ✓  {'awi-core':<36} up to date")
    elif core["status"] == "synced":
        n_drift   = len(core["drift"])
        n_missing = len(core["missing"])
        tags = (" [committed]" if core["committed"] else "") + (" [pushed]" if core["pushed"] else "")
        print(f"  ↓  {'awi-core':<36} {n_drift} drift, {n_missing} missing synced{tags}")
    elif core["status"] == "failed":
        print(f"  ✗  {'awi-core':<36} failed")
        print(f"     → {core['error']}")

    print()
    print("─" * 52)
    print()


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    full_report = "--full-report" in sys.argv   # show Mermaid graph
    breakdown   = "--breakdown"   in sys.argv   # show per-submodule text

    # Step 1: Discover all submodules from .gitmodules files (no git operations yet)
    results = scan()

    # Step 2: If the registry file doesn't exist, create it from scratch.
    #         This happens the first time /awi-sync runs, or after the file is deleted.
    if not REGISTRY_PATH.exists():
        create_registry_file(results)

    # Step 3: Sync each submodule (commit local changes, pull, push).
    #         Also updates the registry table row for each submodule as it completes.
    results = sync_all(results)

    # Step 4: Sync the AWI root repo itself (captures updated submodule pointers)
    root = sync_root()

    # Step 5: Update the Mermaid diagram colors to reflect the final sync state
    update_registry(results, root=root)

    # Step 6: Mirror any changed source files to awi-core dev-claude branch
    core = sync_awi_core()

    # Step 7: Always print 1-line summary
    ok, failed = _count_results(results, root, core)
    exit_code  = print_summary(ok, failed)

    # Step 8: Optional outputs based on flags
    if full_report:
        print_mermaid_graph()
    if breakdown or failed > 0:
        print_breakdown(results, root, core)

    # Step 9: Log the invocation — outcome determined by exit code, no AI needed
    outcome    = "completed" if exit_code == 0 else "errored"
    log_script = Path(__file__).resolve().parents[2] / "shared" / "scripts" / "log_command.py"
    subprocess.run([sys.executable, str(log_script), "awi-sync", outcome])

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
