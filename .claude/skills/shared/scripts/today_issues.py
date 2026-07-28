#!/usr/bin/env python3
"""
today_issues.py — Data layer for /today skill.

Reads the daily file's state, fetches GitHub Issues through fetch_issues.py,
computes the time budget. Outputs JSON to stdout. Claude reads output and routes.

Usage:
    python3 .claude/skills/shared/scripts/today_issues.py
    python3 .claude/skills/shared/scripts/today_issues.py --org newhaze --no-personal

Which trackers to read comes from the daily file's `working-orgs` and
`include-personal` frontmatter, written at morning check-in. The matching CLI
flags override it, which is what check-in itself uses — it must fetch with the
answers it just collected, before it has written them to disk.

Output schema:
{
  "state": "needs_checkin" | "ready" | "done",
  "energy_ceiling": "high" | "medium" | "low" | null,
  "start_time": "HH:MM" | null,
  "end_time": "HH:MM" | null,
  "window_minutes": int | null,
  "available_minutes": int | null,
  "working_orgs": [str, ...] | null,   # null = every active org
  "include_personal": bool,
  "pinned": [Issue, ...],
  "issues": [Issue, ...],
  "errors": [str, ...]
}

Issue shape: as returned by fetch_issues.normalise, plus:
{
  "excerpt": str | null,       # first meaningful line, truncated (display hint)
}
"""

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import AWI_ROOT
from current_user import resolve_github_id
from fetch_issues import fetch_all_issues

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


# ── Scope ─────────────────────────────────────────────────────────────────────

def resolve_scope(
    fm: dict, cli_orgs: list[str] | None, cli_personal: bool | None
) -> tuple[list[str] | None, bool]:
    """Which trackers to read: CLI flags first, else the daily frontmatter.

    working-orgs absent (or not a list) means every active org — the state of a
    day checked in before org selection existed, and the sane default.
    """
    if cli_orgs is not None:
        orgs = cli_orgs
    else:
        declared = fm.get("working-orgs")
        orgs = [str(o) for o in declared] if isinstance(declared, list) else None

    if cli_personal is not None:
        include_personal = cli_personal
    else:
        include_personal = bool(fm.get("include-personal", True))

    return orgs, include_personal


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--working-date", default=None,
                        help="YYYY-MM-DD working date (default: today)")
    parser.add_argument("--org", action="append", dest="orgs", default=None,
                        help="override working-orgs from the daily file (repeatable)")
    parser.add_argument("--personal", action="store_true", dest="personal", default=None,
                        help="force-include the personal repo")
    parser.add_argument("--no-personal", action="store_false", dest="personal",
                        help="force-exclude the personal repo")
    args, _ = parser.parse_known_args()

    # Resolve user paths
    github_id = resolve_github_id()
    user_root = AWI_ROOT / "_data" / "users" / github_id

    # Resolve working date (supports day_start_hour boundary from SKILL.md)
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

    # Fetch issues from the trackers this day is scoped to
    working_orgs, include_personal = resolve_scope(fm, args.orgs, args.personal)
    all_issues, errors = fetch_all_issues(
        orgs=working_orgs,
        include_personal=include_personal,
    )
    for issue in all_issues:
        issue["excerpt"] = extract_excerpt(issue["body"])

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
        "working_orgs": working_orgs,
        "include_personal": include_personal,
        "pinned": pinned,
        "issues": issues,
        "errors": errors,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
