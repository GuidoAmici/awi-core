#!/usr/bin/env python3
"""AWI manifest layer — what a workspace is made of, and what this operator wants.

Two manifests, two owners:

  user-submodules.json   in _data/users/<github-id>/ — private to one operator.
      Which orgs and system repos they materialise, with url/path/branch for
      each, plus which of an org's codebases they want on disk.

  codebases.json         in _data/organizations/<org>/ — versioned in the org
      workspace, shared by everyone working that org. The record of which repos
      make up the org and on what branch.

The split is the point: a workspace repo should tell any collaborator what it is
made of, while nobody's private choice of what to check out leaks into it.

Nothing here is a git submodule. Every entry is materialised by `git clone`, so
no gitlink can pin a commit that exists on a single machine, and no repo ever
swallows another repo's code. See ADR 0009.
"""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

CODEBASES_FILE = "codebases.json"
CODEBASE_SUBDIR = "codebase"


@dataclass(frozen=True)
class Repo:
    """One repo to materialise, with everything needed to clone it."""

    name: str
    url: str
    branch: str
    path: Path  # absolute
    parent: str  # "AWI" for top-level entries, else the org name
    upstream: bool = False  # read-only mirror of a third-party repo: never push

    @property
    def is_codebase(self) -> bool:
        return self.parent != "AWI"


# ── user-submodules.json ──────────────────────────────────────────────────────

def load_submodules(awi_root: Path) -> tuple[dict, str, str]:
    """Return (entries, github_id, user_repo) for the logged-in operator."""
    users_dir = awi_root / "_data" / "users"
    current_user_file = users_dir / "current-user.json"

    if not current_user_file.exists():
        raise FileNotFoundError(
            "_data/users/current-user.json not found — run /awi-user to log in"
        )

    current_user = json.loads(current_user_file.read_text())
    github_id = str(current_user["github-id"])
    login = current_user["login"]
    user_repo = current_user.get("user_repo", f"{login}/my-awi-user")

    submodules_file = users_dir / github_id / "user-submodules.json"
    raw = json.loads(submodules_file.read_text()) if submodules_file.exists() else {}
    return raw, github_id, user_repo


def entry_type(entry: dict) -> str:
    """Resolve an entry's type, falling back to the legacy path convention."""
    declared = entry.get("type")
    if declared:
        return declared
    path = entry.get("path", "")
    return "org-workspace" if path.startswith("_data/organizations/") else "system-repo"


def active_entries(raw: dict) -> dict:
    return {k: v for k, v in raw.items() if v.get("active", False)}


def inactive_entries(raw: dict) -> dict:
    return {k: v for k, v in raw.items() if not v.get("active", False)}


def active_codebases(entry: dict) -> list[str] | None:
    """Which codebases of one org this operator wants on disk.

    Three distinct answers, so callers can tell "never curated" from "chose none":

      None  — no `codebases` key: take everything the org declares.
      []    — the key exists but nothing in it is active: the operator wants the
              workspace with no code checked out.
      [...] — exactly these, by name.
    """
    codebases = entry.get("codebases")
    if codebases is None:
        return None
    return [name for name, cb in codebases.items() if cb.get("active", False)]


# ── codebases.json ────────────────────────────────────────────────────────────

def load_codebases(org_root: Path) -> dict:
    """Read one org workspace's shared codebase manifest. Missing file → {}."""
    manifest = org_root / CODEBASES_FILE
    if not manifest.exists():
        return {}
    return json.loads(manifest.read_text())


# ── Materialisation ───────────────────────────────────────────────────────────

def is_repo(path: Path) -> bool:
    return (path / ".git").exists()


def is_mounted(path: Path) -> bool:
    """True if the directory holds anything at all."""
    return path.exists() and any(path.iterdir())


def materialise_target(path: Path, url: str, branch: str) -> tuple[str, str | None]:
    """Clone `url` into `path` unless it is already there. Returns (status, error).

    status is "cloned", "present" or "failed".

    An existing checkout is left exactly as it is — materialising must never move
    the operator off the branch they are working on. context_sync.py owns that.
    """
    if is_repo(path):
        return "present", None

    if is_mounted(path):
        return "failed", (
            f"{path} already holds files but is not a git repo — "
            "move it aside and re-run"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    rc = subprocess.run(
        ["git", "clone", "--branch", branch, url, str(path)],
        capture_output=True,
        text=True,
    )
    if rc.returncode != 0:
        return "failed", rc.stderr.strip()
    return "cloned", None


# ── Resolution ────────────────────────────────────────────────────────────────

def resolve_org_codebases(
    awi_root: Path, org_name: str, entry: dict
) -> tuple[list[Repo], list[str]]:
    """Resolve one org's wanted codebases into clone targets.

    Returns (repos, unknown) where `unknown` names codebases the operator asked
    for that the org's codebases.json does not declare — a real mismatch worth
    surfacing rather than silently skipping.
    """
    org_root = awi_root / entry["path"]
    declared = load_codebases(org_root)
    wanted = active_codebases(entry)

    if wanted is None:
        wanted = list(declared)

    repos: list[Repo] = []
    unknown: list[str] = []
    for name in wanted:
        spec = declared.get(name)
        if spec is None:
            unknown.append(name)
            continue
        repos.append(
            Repo(
                name=name,
                url=spec["url"],
                branch=spec.get("branch", "main"),
                path=org_root / CODEBASE_SUBDIR / name,
                parent=org_name,
            )
        )
    return repos, unknown


def plan(awi_root: Path) -> tuple[list[Repo], list[str]]:
    """Everything this operator wants materialised, in clone order.

    Orgs and system repos come first, then each org's codebases — a codebase
    cannot be resolved until its org workspace is on disk, because that is where
    codebases.json lives.

    Returns (repos, warnings).
    """
    raw, github_id, user_repo = load_submodules(awi_root)
    active = active_entries(raw)

    top: list[Repo] = []
    for name, entry in active.items():
        top.append(
            Repo(
                name=name,
                url=entry["url"],
                branch=entry.get("branch", "only"),
                path=awi_root / entry["path"],
                parent="AWI",
                upstream=entry.get("upstream", False),
            )
        )

    # The operator's own repo is resolved from current-user.json, never from
    # user-submodules.json — it is the one entry they cannot toggle off.
    top.append(
        Repo(
            name=github_id,
            url=f"https://github.com/{user_repo}.git",
            branch="only",
            path=awi_root / "_data" / "users" / github_id,
            parent="AWI",
        )
    )

    codebases: list[Repo] = []
    warnings: list[str] = []
    for name, entry in active.items():
        if entry_type(entry) != "org-workspace":
            continue
        org_root = awi_root / entry["path"]
        if not (org_root / CODEBASES_FILE).exists():
            # Expected before the org is cloned; the caller re-plans afterwards.
            continue
        repos, unknown = resolve_org_codebases(awi_root, name, entry)
        codebases.extend(repos)
        for cb in unknown:
            warnings.append(
                f"{name}: '{cb}' is active in user-submodules.json but not "
                f"declared in {name}/{CODEBASES_FILE}"
            )

    return top + codebases, warnings
