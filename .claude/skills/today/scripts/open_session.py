#!/usr/bin/env python3
"""
open_session.py — Prompt when a previous session is still open.

Usage:
    python3 .claude/skills/today/scripts/open_session.py \
        --day-name Friday --working-date 2026-05-08

Output JSON:
    {"action": "continue"} | {"action": "close_start"}
"""
import argparse
import curses
import json
import os
import sys

PAIR_HEADER = 1
PAIR_CURSOR = 2
PAIR_DIM    = 3
PAIR_FOOTER = 4
PAIR_TITLE  = 5


def setup_colors() -> None:
    curses.start_color()
    curses.use_default_colors()
    bg = -1
    curses.init_pair(PAIR_HEADER, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(PAIR_CURSOR, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(PAIR_DIM,    curses.COLOR_WHITE, bg)
    curses.init_pair(PAIR_FOOTER, curses.COLOR_WHITE, bg)
    curses.init_pair(PAIR_TITLE,  curses.COLOR_CYAN,  bg)


def run(stdscr, day_name: str) -> str:
    curses.curs_set(0)
    setup_colors()

    options = [
        (f"Continue {day_name}'s session",
         f"Keep working in {day_name}'s context"),
        (f"Close {day_name} and start today",
         f"Run {day_name}'s retrospective, then start a fresh day"),
    ]
    cursor = 0

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        # Header
        hdr = " /today — Open Session"
        stdscr.attron(curses.color_pair(PAIR_HEADER) | curses.A_BOLD)
        stdscr.addnstr(0, 0, hdr.ljust(w), w)
        stdscr.attroff(curses.color_pair(PAIR_HEADER) | curses.A_BOLD)

        stdscr.attron(curses.color_pair(PAIR_DIM))
        stdscr.addnstr(1, 0, "─" * w, w)
        stdscr.attroff(curses.color_pair(PAIR_DIM))

        # Body
        stdscr.attron(curses.color_pair(PAIR_TITLE) | curses.A_BOLD)
        stdscr.addnstr(3, 2, f"{day_name}'s session is still open.", w - 2)
        stdscr.attroff(curses.color_pair(PAIR_TITLE) | curses.A_BOLD)
        stdscr.addnstr(4, 2, "What do you want to do?", w - 2)

        for i, (label, desc) in enumerate(options):
            row = 6 + i * 3
            if row + 1 >= h - 2:
                break
            is_cur = i == cursor
            marker = ">" if is_cur else " "
            attr = curses.color_pair(PAIR_CURSOR) | curses.A_BOLD if is_cur else curses.A_NORMAL
            stdscr.attron(attr)
            stdscr.addnstr(row, 2, f"{marker} {label}", w - 2)
            stdscr.attroff(attr)
            stdscr.attron(curses.color_pair(PAIR_DIM))
            stdscr.addnstr(row + 1, 6, desc, w - 6)
            stdscr.attroff(curses.color_pair(PAIR_DIM))

        # Footer
        stdscr.attron(curses.color_pair(PAIR_DIM))
        stdscr.addnstr(h - 2, 0, "─" * w, w)
        stdscr.attroff(curses.color_pair(PAIR_DIM))
        stdscr.attron(curses.color_pair(PAIR_FOOTER))
        stdscr.addnstr(h - 1, 0, " ↑↓ navigate   ENTER select   Q quit".ljust(w), w)
        stdscr.attroff(curses.color_pair(PAIR_FOOTER))

        stdscr.refresh()
        key = stdscr.getch()

        if key in (ord("q"), ord("Q"), 27):
            return "continue"
        elif key == curses.KEY_UP:
            cursor = max(0, cursor - 1)
        elif key == curses.KEY_DOWN:
            cursor = min(len(options) - 1, cursor + 1)
        elif key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
            return "continue" if cursor == 0 else "close_start"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--day-name",     required=True, help="e.g. Friday")
    parser.add_argument("--working-date", required=True, help="YYYY-MM-DD")
    args = parser.parse_args()

    tty_fd   = os.open("/dev/tty", os.O_RDWR)
    old_stdin = os.dup(0)
    os.dup2(tty_fd, 0)
    os.close(tty_fd)
    try:
        action = curses.wrapper(lambda scr: run(scr, args.day_name))
    finally:
        os.dup2(old_stdin, 0)
        os.close(old_stdin)

    print(json.dumps({"action": action}))


if __name__ == "__main__":
    main()
