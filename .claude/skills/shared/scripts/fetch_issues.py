#!/usr/bin/env python3
"""fetch_issues.py — the one place AWI reads issues from GitHub.

Every skill that needs issues goes through here, so a run costs one authorised
call instead of one per org. Two ways in:

    import  — fetch_all_issues(orgs=..., labels=..., include_personal=...)
    CLI     — python3 fetch_issues.py [--org NAME]... [--label NAME]... [--no-personal]

Where issues live follows from the manifest, not from a second registry:
`user-submodules.json` entries typed `org-workspace` and marked active name the
org trackers, and each one's GitHub slug is derived from its `url` at runtime.
The operator's own repo holds personal issues and nothing else — there is no
cross-org routing, no `org:` label to interpret. See ADR 0006.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import AWI_ROOT
from manifest import active_entries, entry_type, load_submodules

GH_FIELDS = ["number", "title", "labels", "body"]
GH_LIMIT = "200"


# ── Slug derivation ───────────────────────────────────────────────────────────

def repo_slug(url: str) -> str | None:
    """`https://github.com/Owner/repo.git` → `Owner/repo`. None if unparseable.

    Tolerates SSH remotes and a missing `.git`, because a manifest edited by
    hand is a normal thing to encounter.
    """
    if not url:
        return None
    cleaned = url.strip().removesuffix(".git")
    match = re.search(r"github\.com[:/]+([^/]+)/([^/]+?)/?$", cleaned)
    if not match:
        return None
    return f"{match.group(1)}/{match.group(2)}"


def org_trackers(raw: dict, orgs: list[str] | None = None) -> tuple[dict, list[str]]:
    """Map org name → GitHub slug for the active org workspaces.

    `orgs` narrows the result to those names; None means every active one.
    Returns (trackers, errors) — an org that is asked for but not active, or
    whose url yields no slug, is reported rather than silently dropped.
    """
    trackers: dict[str, str] = {}
    errors: list[str] = []

    active = {
        name: entry
        for name, entry in active_entries(raw).items()
        if entry_type(entry) == "org-workspace"
    }

    for name, entry in active.items():
        if orgs is not None and name not in orgs:
            continue
        slug = repo_slug(entry.get("url", ""))
        if slug is None:
            errors.append(
                f"org '{name}': cannot derive a GitHub repo from url "
                f"{entry.get('url', '(missing)')!r} in user-submodules.json"
            )
            continue
        trackers[name] = slug

    for name in orgs or []:
        if name not in active:
            errors.append(
                f"org '{name}' was requested but is not an active "
                f"org-workspace in user-submodules.json"
            )

    return trackers, errors


# ── Normalisation ─────────────────────────────────────────────────────────────

def label_value(label_names: list[str], prefix: str) -> str | None:
    for name in label_names:
        if name.startswith(prefix):
            return name[len(prefix):]
    return None


def normalise(raw: dict, source_repo: str, org: str | None) -> dict:
    """One GitHub issue in AWI's canonical shape.

    `org` is the tracker the issue came from — an org name, or None for the
    operator's personal repo. It is never read off a label.
    """
    label_names = [lb["name"] for lb in raw.get("labels", [])]
    issue = {
        "number": raw["number"],
        "title": raw["title"],
        "body": raw.get("body") or "",
        "org": org,
        "repo": label_value(label_names, "repo:"),
        "project": label_value(label_names, "project:"),
        "priority": label_value(label_names, "priority:") or "medium",
        "energy": label_value(label_names, "energy:") or "medium",
        "duration": label_value(label_names, "duration:"),
        "labels": label_names,
        "pinned": "pinned" in label_names,
        "source_repo": source_repo,
    }
    if "comments" in raw:
        issue["comments"] = raw["comments"]
    return issue


# ── Fetching ──────────────────────────────────────────────────────────────────

def fetch_repo_issues(
    source_repo: str,
    org: str | None,
    labels: list[str] | None = None,
    include_comments: bool = False,
) -> tuple[list[dict], list[str]]:
    """Open issues from one repo. A failed fetch yields an error, never raises.

    Multiple `--label` values are AND-ed by `gh`, matching its own semantics.
    """
    fields = (GH_FIELDS + ["comments"]) if include_comments else GH_FIELDS
    cmd = [
        "gh", "issue", "list",
        "--repo", source_repo,
        "--state", "open",
        "--limit", GH_LIMIT,
        "--json", ",".join(fields),
    ]
    for label in labels or []:
        cmd += ["--label", label]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return [], [f"gh issue list failed for {source_repo}: {result.stderr.strip()}"]

    try:
        raw_list = json.loads(result.stdout or "[]")
    except json.JSONDecodeError as exc:
        return [], [f"gh issue list returned invalid JSON for {source_repo}: {exc}"]

    return [normalise(raw, source_repo, org) for raw in raw_list], []


def fetch_all_issues(
    orgs: list[str] | None = None,
    labels: list[str] | None = None,
    include_personal: bool = True,
    include_comments: bool = False,
    awi_root: Path = AWI_ROOT,
) -> tuple[list[dict], list[str]]:
    """Issues across the operator's active org trackers, plus their own repo.

    orgs             — restrict to these org names; None means all active ones.
    labels           — only issues carrying every one of these labels.
    include_personal — whether to also read the operator's personal repo.
    include_comments — attach each issue's comments; off by default because
                       only /delegate-issue needs them and they are bulky.

    Returns (issues, errors). One unreachable tracker degrades that tracker
    only; the rest of the day's issues still come back.
    """
    raw, _github_id, user_repo = load_submodules(awi_root)
    trackers, errors = org_trackers(raw, orgs)

    targets = [(slug, name) for name, slug in trackers.items()]
    if include_personal and user_repo:
        targets.append((user_repo, None))

    issues: list[dict] = []
    for slug, org_name in targets:
        found, errs = fetch_repo_issues(
            slug, org=org_name, labels=labels, include_comments=include_comments
        )
        issues.extend(found)
        errors.extend(errs)

    return issues, errors


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--org", action="append", dest="orgs", default=None,
                        help="restrict to this org (repeatable; default: all active)")
    parser.add_argument("--label", action="append", dest="labels", default=None,
                        help="only issues carrying this label (repeatable, AND-ed)")
    parser.add_argument("--no-personal", action="store_false", dest="include_personal",
                        help="skip the operator's personal repo")
    parser.add_argument("--comments", action="store_true", dest="include_comments",
                        help="attach each issue's comments (needed for agent briefs)")
    args = parser.parse_args()

    issues, errors = fetch_all_issues(
        orgs=args.orgs,
        labels=args.labels,
        include_personal=args.include_personal,
        include_comments=args.include_comments,
    )
    print(json.dumps({"issues": issues, "errors": errors},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
