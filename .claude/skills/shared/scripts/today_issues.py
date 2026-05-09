#!/usr/bin/env python3
"""
today_issues.py — Data layer for /today skill.

Reads active orgs + daily file state, fetches GitHub Issues, computes
time budget. Outputs JSON to stdout. Claude reads output and routes.

Usage:
    python3 .claude/skills/shared/scripts/today_issues.py

Output schema:
{
  "state": "needs_checkin" | "ready" | "done",
  "energy_ceiling": "high" | "medium" | "low" | null,
  "start_time": "HH:MM" | null,
  "end_time": "HH:MM" | null,
  "window_minutes": int | null,
  "available_minutes": int | null,
  "pinned": [Issue, ...],
  "issues": [Issue, ...],
  "errors": [str, ...]
}

Issue shape:
{
  "number": int,
  "title": str,
  "excerpt": str | null,
  "org": str | null,          # value of org: label (null = personal/cross-org)
  "repo": str | null,          # value of repo: label (codebase context)
  "project": str | null,       # value of project: label
  "priority": "high" | "medium" | "low",
  "energy": "high" | "medium" | "low",
  "duration": "15m" | "30m" | "1h" | "2h" | "3h+" | null,
  "pinned": bool,
  "source_repo": str           # GitHub repo slug where issue lives
}
"""

import json
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import AWI_ROOT
from current_user import resolve_github_id

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_duration_minutes(duration: str | None) -> int | None:
    if not duration:
        return None
    d = duration.lower().strip()
    if d == "3h+":
        return 180
    h = re.search(r"(\d+)h", d)
    m = re.search(r"(\d+)m", d)
    total = 0
    if h:
        total += int(h.group(1)) * 60
    if m:
        total += int(m.group(1))
    return total if total else None


def label_value(label_names: list[str], prefix: str) -> str | None:
    for name in label_names:
        if name.startswith(prefix):
            return name[len(prefix):]
    return None


def extract_excerpt(body: str | None) -> str | None:
    if not body:
        return None
    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith("|") or line.startswith("---"):
            continue
        if line.startswith("```") or line.startswith(">"):
            continue
        # Strip common markdown
        line = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
        line = re.sub(r"\*(.+?)\*", r"\1", line)
        line = re.sub(r"`(.+?)`", r"\1", line)
        line = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", line)
        line = line.strip(" -")
        if len(line) > 15:
            return line[:150] + ("…" if len(line) > 150 else "")
    return None


def parse_time(t: str | None) -> datetime | None:
    if not t:
        return None
    try:
        return datetime.strptime(str(t).strip(), "%H:%M")
    except ValueError:
        return None


def parse_frontmatter(text: str) -> dict:
    text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    if yaml:
        try:
            return yaml.safe_load(parts[1]) or {}
        except Exception:
            return {}
    # Minimal fallback: key: value lines
    fm = {}
    for line in parts[1].splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def parse_scheduled_minutes(content: str) -> int:
    """Sum durations of scheduled blocks from ## Morning Check-in."""
    total = 0
    in_section = False
    for line in content.splitlines():
        if re.search(r"\*\*Scheduled blocks", line) or "Scheduled blocks:" in line:
            in_section = True
            continue
        if in_section:
            if re.match(r"\s*\*\*", line) or re.match(r"\s*#{1,6} ", line):
                break
            h = sum(int(x) for x in re.findall(r"(\d+)h", line))
            m = sum(int(x) for x in re.findall(r"(\d+)m", line))
            total += h * 60 + m
    return total


def parse_completed_minutes(content: str, issues: list[dict]) -> int:
    """Sum durations of [x]-checked issues in the daily file."""
    # Build ref → duration_minutes map
    dur_map: dict[str, int] = {}
    for issue in issues:
        ref = f"{issue['source_repo'].split('/')[-1]}#{issue['number']}"
        mins = parse_duration_minutes(issue.get("duration"))
        if mins:
            dur_map[ref] = mins

    total = 0
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- [x]"):
            continue
        for ref, mins in dur_map.items():
            if ref in line:
                total += mins
                break
    return total


# ── GitHub fetch ──────────────────────────────────────────────────────────────

def fetch_issues(
    source_repo: str,
    default_org: str | None,
    active_org_names: list[str] | None = None,
) -> tuple[list[dict], list[str]]:
    """
    Fetch open issues from source_repo.

    default_org: if set, all issues get this org value (workspace repo case).
    active_org_names: if set, filter cross-org issues by active org labels
                      (user_repo case). Issues with no org: label are always kept.
    """
    cmd = [
        "gh", "issue", "list",
        "--repo", source_repo,
        "--state", "open",
        "--limit", "200",
        "--json", "number,title,labels,body",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return [], [f"gh issue list failed for {source_repo}: {result.stderr.strip()}"]

    raw_list = json.loads(result.stdout or "[]")
    issues = []
    for raw in raw_list:
        label_names = [lb["name"] for lb in raw.get("labels", [])]

        # Determine org
        if default_org is not None:
            org = default_org
        else:
            # Cross-org: read from org: label
            org = label_value(label_names, "org:")
            # Filter: skip if org is set but not active
            if org is not None and active_org_names is not None:
                if org not in active_org_names:
                    continue

        issues.append({
            "number": raw["number"],
            "title": raw["title"],
            "excerpt": extract_excerpt(raw.get("body")),
            "org": org,
            "repo": label_value(label_names, "repo:"),
            "project": label_value(label_names, "project:"),
            "priority": label_value(label_names, "priority:") or "medium",
            "energy": label_value(label_names, "energy:") or "medium",
            "duration": label_value(label_names, "duration:"),
            "pinned": "pinned" in label_names,
            "source_repo": source_repo,
        })

    return issues, []


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--working-date", default=None,
                        help="YYYY-MM-DD working date (default: today)")
    args, _ = parser.parse_known_args()

    errors: list[str] = []

    # Resolve user paths
    github_id = resolve_github_id()
    user_root = AWI_ROOT / "_data" / "users" / github_id
    current_user_path = AWI_ROOT / "_data" / "users" / "current-user.json"
    current_user = json.loads(current_user_path.read_text())
    user_repo: str | None = current_user.get("user_repo")

    # Read active orgs
    active_orgs_path = user_root / "active-orgs.json"
    active_orgs: dict = json.loads(active_orgs_path.read_text()) if active_orgs_path.exists() else {}
    active = {name: cfg for name, cfg in active_orgs.items() if cfg.get("active")}
    active_org_names = list(active.keys())

    # Resolve working date (supports 6am-boundary from SKILL.md)
    today_str = args.working_date if args.working_date else date.today().isoformat()
    daily_path = user_root / "agenda" / "daily" / f"{today_str}.md"
    content = daily_path.read_text() if daily_path.exists() else ""
    fm = parse_frontmatter(content) if content else {}

    # Determine state
    checked_in = bool(fm.get("checked-in", False))
    checked_out = bool(fm.get("checked-out", False))
    if not content or not checked_in:
        state = "needs_checkin"
    elif checked_out:
        state = "done"
    else:
        state = "ready"

    energy_ceiling: str | None = fm.get("energy-ceiling") if state != "needs_checkin" else None

    # Time budget (null if no check-in yet)
    start_time_str: str | None = str(fm["start-time"]) if fm.get("start-time") else None
    end_time_str: str | None = str(fm["end-time"]) if fm.get("end-time") else None
    start_dt = parse_time(start_time_str)
    end_dt = parse_time(end_time_str)
    window_minutes: int | None = None
    available_minutes: int | None = None
    if start_dt and end_dt and end_dt > start_dt:
        window_minutes = int((end_dt - start_dt).total_seconds() / 60)

    # Fetch issues from all active workspace repos
    all_issues: list[dict] = []
    for org_name, cfg in active.items():
        workspace_repo = cfg.get("workspace_repo")
        if not workspace_repo:
            errors.append(f"No workspace_repo configured for org '{org_name}' in active-orgs.json")
            continue
        issues, errs = fetch_issues(workspace_repo, default_org=org_name)
        all_issues.extend(issues)
        errors.extend(errs)

    # Fetch cross-org issues from user_repo
    if user_repo:
        cross_issues, errs = fetch_issues(
            user_repo,
            default_org=None,
            active_org_names=active_org_names,
        )
        all_issues.extend(cross_issues)
        errors.extend(errs)

    # Compute available_minutes now that we have issue durations for completed tracking
    if window_minutes is not None:
        scheduled = parse_scheduled_minutes(content)
        completed = parse_completed_minutes(content, all_issues)
        available_minutes = window_minutes - scheduled - completed

    # Split pinned / non-pinned
    pinned = [i for i in all_issues if i["pinned"]]
    issues = [i for i in all_issues if not i["pinned"]]

    print(json.dumps({
        "state": state,
        "energy_ceiling": energy_ceiling,
        "start_time": start_time_str,
        "end_time": end_time_str,
        "window_minutes": window_minutes,
        "available_minutes": available_minutes,
        "pinned": pinned,
        "issues": issues,
        "errors": errors,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
