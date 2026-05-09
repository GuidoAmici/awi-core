#!/usr/bin/env python3
"""
task_picker.py — Interactive curses task picker for /today Q4.

Reads today_issues.py JSON from stdin.
Displays scrollable issue list; description shown only on hovered row.
Hard cap: 3 selections.
Outputs JSON array of selected issues to stdout on confirm.

Usage:
    python3 .claude/skills/shared/scripts/today_issues.py \
      | python3 .claude/skills/today/scripts/task_picker.py
"""

import curses
import json
import sys


MAX_SELECT = 3

# Curses color pair IDs
PAIR_HEADER    = 1
PAIR_SELECTED  = 2
PAIR_CURSOR    = 3
PAIR_CURSOR_SEL = 4
PAIR_DIM       = 5
PAIR_EXCERPT   = 6
PAIR_WARNING   = 7
PAIR_FOOTER    = 8


def load_issues(data: dict) -> list[dict]:
    pinned = data.get("pinned", [])
    issues = data.get("issues", [])
    # Pinned first, then sorted by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    rest = sorted(issues, key=lambda i: priority_order.get(i.get("priority", "medium"), 1))
    return pinned + rest


def fmt_meta(issue: dict) -> str:
    parts = []
    if issue.get("org"):
        parts.append(issue["org"])
    p = issue.get("priority", "medium")
    if p == "high":
        parts.append("!")
    d = issue.get("duration")
    if d:
        parts.append(d)
    return "  ".join(parts)


def filter_issues(issues: list[dict], query: str) -> list[dict]:
    if not query:
        return issues
    q = query.lower()
    return [i for i in issues if q in i.get("title", "").lower()]


def draw(stdscr, issues: list[dict], cursor: int, selected: set,
         scroll: int, warning: str, filter_text: str = ""):
    stdscr.erase()
    h, w = stdscr.getmaxyx()

    # Reserve rows: 3 header + 1 filter + 1 excerpt + 2 footer = 7
    HEADER_ROWS = 3
    FILTER_ROWS = 1
    EXCERPT_ROWS = 2
    FOOTER_ROWS = 2
    list_rows = max(1, h - HEADER_ROWS - FILTER_ROWS - EXCERPT_ROWS - FOOTER_ROWS)

    # ── Header ──────────────────────────────────────────────────────────────
    title = f" Q4 — Commit to today  (select up to {MAX_SELECT})"
    stdscr.attron(curses.color_pair(PAIR_HEADER) | curses.A_BOLD)
    stdscr.addnstr(0, 0, title.ljust(w), w)
    stdscr.attroff(curses.color_pair(PAIR_HEADER) | curses.A_BOLD)

    count_str = f" {len(selected)}/{MAX_SELECT} selected "
    col = max(0, w - len(count_str))
    stdscr.attron(curses.color_pair(PAIR_HEADER) | curses.A_BOLD)
    stdscr.addnstr(0, col, count_str, w - col)
    stdscr.attroff(curses.color_pair(PAIR_HEADER) | curses.A_BOLD)

    sep = "─" * w
    stdscr.attron(curses.color_pair(PAIR_DIM))
    stdscr.addnstr(1, 0, sep, w)
    stdscr.attroff(curses.color_pair(PAIR_DIM))

    if warning:
        stdscr.attron(curses.color_pair(PAIR_WARNING) | curses.A_BOLD)
        stdscr.addnstr(2, 0, f" {warning}".ljust(w), w)
        stdscr.attroff(curses.color_pair(PAIR_WARNING) | curses.A_BOLD)
    else:
        stdscr.addnstr(2, 0, "", 0)  # blank row

    # ── Filter bar ───────────────────────────────────────────────────────────
    filter_prompt = " Filter: "
    filter_display = (filter_text or "")[-max(1, w - len(filter_prompt) - 1):]
    filter_line = f"{filter_prompt}{filter_display}"
    stdscr.attron(curses.color_pair(PAIR_EXCERPT))
    stdscr.addnstr(HEADER_ROWS, 0, filter_line.ljust(w), w)
    stdscr.attroff(curses.color_pair(PAIR_EXCERPT))

    # ── Issue list ───────────────────────────────────────────────────────────
    visible = issues[scroll: scroll + list_rows]
    for idx, issue in enumerate(visible):
        row = HEADER_ROWS + FILTER_ROWS + idx
        abs_idx = scroll + idx
        is_cursor = abs_idx == cursor
        is_sel = abs_idx in selected

        checkbox = "[x]" if is_sel else "[ ]"
        meta = fmt_meta(issue)
        # Width budget: 2 indent + 4 checkbox + 1 space + title + meta right-aligned
        meta_w = min(len(meta) + 2, w // 3)
        title_w = max(1, w - 2 - 4 - 1 - meta_w - 1)
        title_str = issue.get("title", "")[:title_w]

        line = f"  {checkbox} {title_str:<{title_w}} {meta:>{meta_w - 1}}"

        if is_cursor and is_sel:
            attr = curses.color_pair(PAIR_CURSOR_SEL) | curses.A_BOLD
        elif is_cursor:
            attr = curses.color_pair(PAIR_CURSOR) | curses.A_BOLD
        elif is_sel:
            attr = curses.color_pair(PAIR_SELECTED)
        else:
            attr = curses.A_NORMAL

        stdscr.attron(attr)
        stdscr.addnstr(row, 0, line.ljust(w), w)
        stdscr.attroff(attr)

    # ── Excerpt ──────────────────────────────────────────────────────────────
    excerpt_row = HEADER_ROWS + FILTER_ROWS + list_rows
    stdscr.attron(curses.color_pair(PAIR_DIM))
    stdscr.addnstr(excerpt_row, 0, "─" * w, w)
    stdscr.attroff(curses.color_pair(PAIR_DIM))

    excerpt = ""
    if 0 <= cursor < len(issues):
        excerpt = issues[cursor].get("excerpt") or ""
    stdscr.attron(curses.color_pair(PAIR_EXCERPT))
    stdscr.addnstr(excerpt_row + 1, 0, f"  {excerpt}"[:w].ljust(w), w)
    stdscr.attroff(curses.color_pair(PAIR_EXCERPT))

    # ── Footer ───────────────────────────────────────────────────────────────
    footer_row = h - FOOTER_ROWS
    stdscr.attron(curses.color_pair(PAIR_DIM))
    stdscr.addnstr(footer_row, 0, "─" * w, w)
    stdscr.attroff(curses.color_pair(PAIR_DIM))

    keys = " ↑↓ navigate   SPACE select   ENTER confirm   type to filter   Q quit"
    stdscr.attron(curses.color_pair(PAIR_FOOTER))
    stdscr.addnstr(footer_row + 1, 0, keys.ljust(w), w)
    stdscr.attroff(curses.color_pair(PAIR_FOOTER))

    stdscr.refresh()


def setup_colors():
    curses.start_color()
    curses.use_default_colors()

    bg = -1  # transparent

    curses.init_pair(PAIR_HEADER,     curses.COLOR_BLACK,  curses.COLOR_CYAN)
    curses.init_pair(PAIR_SELECTED,   curses.COLOR_GREEN,  bg)
    curses.init_pair(PAIR_CURSOR,     curses.COLOR_BLACK,  curses.COLOR_WHITE)
    curses.init_pair(PAIR_CURSOR_SEL, curses.COLOR_BLACK,  curses.COLOR_GREEN)
    curses.init_pair(PAIR_DIM,        curses.COLOR_WHITE,  bg)
    curses.init_pair(PAIR_EXCERPT,    curses.COLOR_YELLOW, bg)
    curses.init_pair(PAIR_WARNING,    curses.COLOR_RED,    bg)
    curses.init_pair(PAIR_FOOTER,     curses.COLOR_WHITE,  bg)


def run(stdscr, all_issues: list[dict]) -> list[dict]:
    curses.curs_set(0)
    setup_colors()

    filter_text = ""
    issues      = all_issues          # currently visible (filtered) list
    # selected stores indices into all_issues (stable across filter changes)
    selected_keys: set = set()        # frozenset of (source_repo, number)
    cursor  = 0
    scroll  = 0
    warning = ""

    def visible_selected(vis: list[dict]) -> set[int]:
        """Indices into vis that are selected."""
        return {i for i, iss in enumerate(vis)
                if (iss.get("source_repo"), iss.get("number")) in selected_keys}

    while True:
        h, _ = stdscr.getmaxyx()
        HEADER_ROWS  = 3
        FILTER_ROWS  = 1
        EXCERPT_ROWS = 2
        FOOTER_ROWS  = 2
        list_rows = max(1, h - HEADER_ROWS - FILTER_ROWS - EXCERPT_ROWS - FOOTER_ROWS)

        # Keep cursor in view
        if cursor < scroll:
            scroll = cursor
        elif cursor >= scroll + list_rows:
            scroll = cursor - list_rows + 1

        vis_sel = visible_selected(issues)
        draw(stdscr, issues, cursor, vis_sel, scroll, warning, filter_text)
        warning = ""

        ch = stdscr.getch()

        if ch in (ord("q"), ord("Q"), 27):    # q / Q / Escape
            return []

        elif ch == curses.KEY_UP:
            cursor = max(0, cursor - 1)

        elif ch == curses.KEY_DOWN:
            cursor = min(len(issues) - 1, cursor + 1)

        elif ch == curses.KEY_PPAGE:           # Page Up
            cursor = max(0, cursor - list_rows)

        elif ch == curses.KEY_NPAGE:           # Page Down
            cursor = min(len(issues) - 1, cursor + list_rows)

        elif ch == ord(" "):
            if issues:
                iss    = issues[cursor]
                iss_id = (iss.get("source_repo"), iss.get("number"))
                if iss_id in selected_keys:
                    selected_keys.discard(iss_id)
                elif len(selected_keys) >= MAX_SELECT:
                    warning = f"Cap reached — deselect one to pick another (max {MAX_SELECT})"
                else:
                    selected_keys.add(iss_id)

        elif ch in (curses.KEY_ENTER, ord("\n"), ord("\r")):
            return [i for i in all_issues
                    if (i.get("source_repo"), i.get("number")) in selected_keys]

        elif ch in (curses.KEY_BACKSPACE, 127, 8):
            if filter_text:
                filter_text = filter_text[:-1]
                issues = filter_issues(all_issues, filter_text)
                cursor = min(cursor, max(0, len(issues) - 1))

        elif 32 <= ch <= 126:
            filter_text += chr(ch)
            issues = filter_issues(all_issues, filter_text)
            cursor = 0
            scroll = 0


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"task_picker: invalid JSON from stdin: {e}\n")
        sys.exit(1)

    issues = load_issues(data)

    if not issues:
        sys.stderr.write("task_picker: no issues to display\n")
        print(json.dumps([]))
        sys.exit(0)

    # Run TUI — must redirect stdin from /dev/tty so curses can read keys
    # even though stdin was piped.
    import os
    tty_fd = os.open("/dev/tty", os.O_RDWR)
    old_stdin = os.dup(0)
    os.dup2(tty_fd, 0)
    os.close(tty_fd)

    try:
        result = curses.wrapper(lambda scr: run(scr, issues))
    finally:
        os.dup2(old_stdin, 0)
        os.close(old_stdin)

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
