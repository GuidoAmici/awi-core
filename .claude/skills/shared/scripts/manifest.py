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
    #: Commit or tag to materialise at, instead of the branch tip. Only meaningful
    #: for a dependency — a repo a third party can change without warning. A
    #: shared context floats on purpose, because its value is being up to date.
    #: See ADR 0012.
    rev: str | None = None

    @property
    def is_codebase(self) -> bool:
        return self.parent != "AWI"

    @property
    def is_pinned(self) -> bool:
        return self.rev is not None


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


def materialise_target(
    path: Path, url: str, branch: str, rev: str | None = None
) -> tuple[str, str | None]:
    """Clone `url` into `path` unless it is already there. Returns (status, error).

    status is "cloned", "present", "drifted" or "failed".

    An existing checkout is left exactly as it is — materialising must never move
    the operator off the branch they are working on. context_sync.py owns that.

    With `rev`, the repo is pinned: it materialises at that commit or tag instead
    of the branch tip, and an existing checkout sitting somewhere else reports
    "drifted" rather than being silently corrected. Fixing drift is a deliberate
    act, not a side effect of materialising. See ADR 0012.
    """
    if is_repo(path):
        if rev is None:
            return "present", None
        return ("present", None) if _at_rev(path, rev) else (
            "drifted",
            f"{path} is pinned to {rev} but sits elsewhere — "
            f"`git -C {path} checkout {rev}` to align, deliberately",
        )

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

    if rev is not None:
        co = subprocess.run(
            ["git", "-C", str(path), "checkout", "--quiet", rev],
            capture_output=True, text=True,
        )
        if co.returncode != 0:
            return "failed", f"cloned but could not check out {rev}: {co.stderr.strip()}"
    return "cloned", None


def _at_rev(path: Path, rev: str) -> bool:
    """True if HEAD resolves to the same commit as `rev`.

    Compares resolved commits, not strings: a tag and its commit are the same
    pin, and reporting drift because one is spelled as a tag would be noise.
    """
    def resolve(what: str) -> str | None:
        r = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--verify", "--quiet", f"{what}^{{commit}}"],
            capture_output=True, text=True,
        )
        return r.stdout.strip() or None

    head, target = resolve("HEAD"), resolve(rev)
    return bool(head and target and head == target)


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
        # `rev` sólo aplica a un system-repo, que es una dependencia. Un org
        # workspace es contexto compartido y flota en la punta a propósito:
        # pinearlo sería congelar lo que su valor exige que esté al día.
        # Ver ADR 0012.
        es_dependencia = entry_type(entry) == "system-repo"
        top.append(
            Repo(
                name=name,
                url=entry["url"],
                branch=entry.get("branch", "only"),
                path=awi_root / entry["path"],
                parent="AWI",
                upstream=entry.get("upstream", False),
                rev=entry.get("rev") if es_dependencia else None,
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
