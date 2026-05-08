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


def draw(stdscr, issues: list[dict], cursor: int, selected: set, scroll: int, warning: str):
    stdscr.erase()
    h, w = stdscr.getmaxyx()

    # Reserve rows: 3 header + 1 excerpt + 2 footer = 6
    HEADER_ROWS = 3
    EXCERPT_ROWS = 2
    FOOTER_ROWS = 2
    list_rows = max(1, h - HEADER_ROWS - EXCERPT_ROWS - FOOTER_ROWS)

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

    # ── Issue list ───────────────────────────────────────────────────────────
    visible = issues[scroll: scroll + list_rows]
    for idx, issue in enumerate(visible):
        row = HEADER_ROWS + idx
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
    excerpt_row = HEADER_ROWS + list_rows
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

    keys = " ↑↓ navigate   SPACE select   ENTER confirm   Q quit"
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


def run(stdscr, issues: list[dict]) -> list[dict]:
    curses.curs_set(0)
    setup_colors()

    cursor   = 0
    selected: set = set()
    scroll   = 0
    warning  = ""

    while True:
        h, _ = stdscr.getmaxyx()
        HEADER_ROWS  = 3
        EXCERPT_ROWS = 2
        FOOTER_ROWS  = 2
        list_rows = max(1, h - HEADER_ROWS - EXCERPT_ROWS - FOOTER_ROWS)

        # Keep cursor in view
        if cursor < scroll:
            scroll = cursor
        elif cursor >= scroll + list_rows:
            scroll = cursor - list_rows + 1

        draw(stdscr, issues, cursor, selected, scroll, warning)
        warning = ""

        key = stdscr.getch()

        if key in (ord("q"), ord("Q"), 27):   # q / Q / Escape
            return []

        elif key == curses.KEY_UP:
            cursor = max(0, cursor - 1)

        elif key == curses.KEY_DOWN:
            cursor = min(len(issues) - 1, cursor + 1)

        elif key == curses.KEY_PPAGE:          # Page Up
            cursor = max(0, cursor - list_rows)

        elif key == curses.KEY_NPAGE:          # Page Down
            cursor = min(len(issues) - 1, cursor + list_rows)

        elif key == ord(" "):
            if cursor in selected:
                selected.discard(cursor)
            elif len(selected) >= MAX_SELECT:
                warning = f"Cap reached — deselect one to pick another (max {MAX_SELECT})"
            else:
                selected.add(cursor)

        elif key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
            return [issues[i] for i in sorted(selected)]


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
