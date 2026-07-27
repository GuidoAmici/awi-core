#!/usr/bin/env python3
"""Generate .gitmodules from current-user.json + user-submodules.json.

.gitmodules is ephemeral — never committed, always regenerated. That holds at
both levels: the AWI root, and each org workspace's own .gitmodules, so one
operator's choice of which codebases to clone never lands in a shared repo.

Call write_gitmodules(awi_root) from any skill or hook.
"""

import json
import sys
from pathlib import Path


def _entry(path: str, url: str, branch: str, upstream: bool = False) -> list[str]:
    lines = [f'[submodule "{path}"]',
             f"\tpath = {path}",
             f"\turl = {url}",
             f"\tbranch = {branch}"]
    if upstream:
        lines.append("\tupstream = true")
    lines.append("")
    return lines


def _section(entries: dict, header: str, comment: str) -> list[str]:
    if not entries:
        return []
    lines = [f"# ─── {header} {'─' * max(0, 76 - len(header))}",
             f"# {comment}", ""]
    for entry in entries.values():
        lines += _entry(entry["path"], entry["url"],
                        entry.get("branch", "only"), entry.get("upstream", False))
    return lines


def load_submodules(awi_root: Path) -> tuple[dict, str, str]:
    """Return (submodules, github_id, user_repo) for the logged-in user."""
    users_dir = awi_root / "_data" / "users"
    current_user_file = users_dir / "current-user.json"

    if not current_user_file.exists():
        raise FileNotFoundError("_data/users/current-user.json not found — run /awi-user to log in")

    current_user = json.loads(current_user_file.read_text())
    github_id    = str(current_user["github-id"])
    login        = current_user["login"]
    user_repo    = current_user.get("user_repo", f"{login}/my-awi-user")

    submodules_file = users_dir / github_id / "user-submodules.json"
    raw = json.loads(submodules_file.read_text()) if submodules_file.exists() else {}
    return raw, github_id, user_repo


def _entry_type(entry: dict) -> str:
    """Resolve an entry's type, falling back to the legacy path convention."""
    declared = entry.get("type")
    if declared:
        return declared
    return "org-workspace" if entry.get("path", "").startswith("_data/organizations/") else "system-repo"


def generate(awi_root: Path) -> str:
    """Return .gitmodules content for the AWI root."""
    raw, github_id, user_repo = load_submodules(awi_root)

    active = {k: v for k, v in raw.items() if v.get("active", False)}
    orgs   = {k: v for k, v in active.items() if _entry_type(v) == "org-workspace"}
    system = {k: v for k, v in active.items() if _entry_type(v) != "org-workspace"}

    lines: list[str] = []
    lines += _section(orgs, "Entities",
        "One repo per company or person — agenda/, documentation/, codebase/.")
    lines += _section(system, "Workframe",
        "Structural framework repos — shared scaffolding or engine dependencies.")

    # Current user submodule is always last (resolved from current-user.json, not user-submodules.json)
    user_path = f"_data/users/{github_id}"
    lines += [
        "# ─── Workflow ─────────────────────────────────────────────────────────────────",
        "# Automation and tooling repos — the current user's workspace.",
        "",
    ]
    lines += _entry(user_path, f"https://github.com/{user_repo}.git", "only")

    return "\n".join(lines)


def active_codebases(entry: dict) -> list[str]:
    """Names of the codebases this operator wants materialised for one org.

    Only the operator's choice lives in user-submodules.json. Each codebase's
    url, path and branch stay in the org workspace's own committed .gitmodules —
    that topology is shared by everyone working the org, and the gitlink is what
    keeps the workspace linking the code instead of duplicating it.

    An org with no `codebases` key means "all of them".
    """
    codebases = entry.get("codebases")
    if codebases is None:
        return []
    return [name for name, cb in codebases.items() if cb.get("active", False)]


def write_gitmodules(awi_root: Path) -> None:
    """Regenerate .gitmodules at the AWI root."""
    (awi_root / ".gitmodules").write_text(generate(awi_root))


if __name__ == "__main__":
    awi_root = Path(__file__).resolve().parents[4]
    try:
        write_gitmodules(awi_root)
        print(".gitmodules regenerated.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
