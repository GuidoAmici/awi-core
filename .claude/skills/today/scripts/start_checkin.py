#!/usr/bin/env python3
"""
start_checkin.py — Morning check-in wizard (Q1–Q3) for /today Start mode.

Usage:
    python3 .claude/skills/today/scripts/start_checkin.py \
        --working-date 2026-05-09 --current-time 06:17

Output JSON:
    {
        "energy": "high" | "medium" | "low",
        "start_time": "HH:MM",
        "end_time": "HH:MM",
        "scheduled_blocks": [{"description": "...", "duration": "..."}]
    }
Exit 1 if the user quits without completing.
"""
import argparse
import curses
import json
import os
import re
import sys

# ── Colour pairs ──────────────────────────────────────────────────────────────
PAIR_HEADER  = 1
PAIR_CURSOR  = 2
PAIR_DIM     = 3
PAIR_FOOTER  = 4
PAIR_TITLE   = 5
PAIR_ADDED   = 6
PAIR_INPUT   = 7
PAIR_ERROR   = 8


def setup_colors() -> None:
    curses.start_color()
    curses.use_default_colors()
    bg = -1
    curses.init_pair(PAIR_HEADER, curses.COLOR_BLACK,  curses.COLOR_CYAN)
    curses.init_pair(PAIR_CURSOR, curses.COLOR_BLACK,  curses.COLOR_WHITE)
    curses.init_pair(PAIR_DIM,    curses.COLOR_WHITE,  bg)
    curses.init_pair(PAIR_FOOTER, curses.COLOR_WHITE,  bg)
    curses.init_pair(PAIR_TITLE,  curses.COLOR_CYAN,   bg)
    curses.init_pair(PAIR_ADDED,  curses.COLOR_GREEN,  bg)
    curses.init_pair(PAIR_INPUT,  curses.COLOR_YELLOW, bg)
    curses.init_pair(PAIR_ERROR,  curses.COLOR_RED,    bg)


# ── Shared drawing helpers ─────────────────────────────────────────────────────

def draw_frame(stdscr, step: int, total: int, question: str) -> None:
    h, w = stdscr.getmaxyx()
    step_str = f" Step {step} of {total} "
    hdr = " /today — Morning Check-in"
    stdscr.attron(curses.color_pair(PAIR_HEADER) | curses.A_BOLD)
    stdscr.addnstr(0, 0, hdr.ljust(w - len(step_str)), w - len(step_str))
    stdscr.addnstr(0, max(0, w - len(step_str)), step_str, len(step_str))
    stdscr.attroff(curses.color_pair(PAIR_HEADER) | curses.A_BOLD)

    stdscr.attron(curses.color_pair(PAIR_DIM))
    stdscr.addnstr(1, 0, "─" * w, w)
    stdscr.attroff(curses.color_pair(PAIR_DIM))

    stdscr.attron(curses.color_pair(PAIR_TITLE) | curses.A_BOLD)
    stdscr.addnstr(3, 2, question, w - 2)
    stdscr.attroff(curses.color_pair(PAIR_TITLE) | curses.A_BOLD)

    stdscr.attron(curses.color_pair(PAIR_DIM))
    stdscr.addnstr(h - 2, 0, "─" * w, w)
    stdscr.attroff(curses.color_pair(PAIR_DIM))
    stdscr.attron(curses.color_pair(PAIR_FOOTER))
    stdscr.addnstr(h - 1, 0,
                   " ↑↓ navigate   ENTER select   ESC/Q quit".ljust(w), w)
    stdscr.attroff(curses.color_pair(PAIR_FOOTER))


def draw_options(stdscr, options: list[tuple[str, str]],
                 cursor: int, start_row: int = 5) -> None:
    h, w = stdscr.getmaxyx()
    for i, (label, desc) in enumerate(options):
        row = start_row + i * 2
        if row + 1 >= h - 2:
            break
        is_cur = i == cursor
        marker = ">" if is_cur else " "
        attr = curses.color_pair(PAIR_CURSOR) | curses.A_BOLD if is_cur else curses.A_NORMAL
        stdscr.attron(attr)
        stdscr.addnstr(row, 2, f"{marker} {label}", w - 2)
        stdscr.attroff(attr)
        if desc:
            stdscr.attron(curses.color_pair(PAIR_DIM))
            stdscr.addnstr(row + 1, 6, desc, w - 6)
            stdscr.attroff(curses.color_pair(PAIR_DIM))


def get_text_input(stdscr, row: int, col: int, width: int,
                   prompt: str = "") -> str | None:
    """Inline text input. Returns string on Enter, None on Escape."""
    h, w = stdscr.getmaxyx()
    if prompt:
        stdscr.addnstr(row, col, prompt, max(0, w - col))
        col = min(col + len(prompt), w - 2)
    curses.curs_set(1)
    buf: list[str] = []

    while True:
        field   = "".join(buf)
        display = field[-width:] if len(field) >= width else field
        padded  = display.ljust(width)
        avail   = min(width, max(0, w - col))
        if avail > 0:
            stdscr.attron(curses.color_pair(PAIR_INPUT) | curses.A_UNDERLINE)
            stdscr.addnstr(row, col, padded[:avail], avail)
            stdscr.attroff(curses.color_pair(PAIR_INPUT) | curses.A_UNDERLINE)
        cx = min(col + len(display), w - 1)
        try:
            stdscr.move(row, cx)
        except curses.error:
            pass
        stdscr.refresh()

        key = stdscr.getch()
        if key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
            curses.curs_set(0)
            return "".join(buf)
        elif key == 27:
            curses.curs_set(0)
            return None
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if buf:
                buf.pop()
        elif 32 <= key <= 126:
            buf.append(chr(key))


# ── Step implementations ───────────────────────────────────────────────────────

def step_energy(stdscr) -> str | None:
    options = [
        ("Great!", "High energy — all task types available"),
        ("Okay",   "Medium energy — high-energy tasks flagged, avoid in afternoon"),
        ("Low",    "Low energy — only low/medium tasks; high-energy deferred"),
    ]
    energy_map = {"Great!": "high", "Okay": "medium", "Low": "low"}
    cursor = 0

    while True:
        stdscr.erase()
        draw_frame(stdscr, 1, 3, "How are you feeling right now?")
        draw_options(stdscr, options, cursor)
        stdscr.refresh()

        key = stdscr.getch()
        if key in (ord("q"), ord("Q"), 27):
            return None
        elif key == curses.KEY_UP:
            cursor = max(0, cursor - 1)
        elif key == curses.KEY_DOWN:
            cursor = min(len(options) - 1, cursor + 1)
        elif key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
            return energy_map[options[cursor][0]]


def parse_time(s: str) -> str | None:
    s = s.strip()
    m = re.match(r"^(\d{1,2}):(\d{2})$", s)
    if m:
        hh, mm = int(m.group(1)), int(m.group(2))
        if 0 <= hh <= 23 and 0 <= mm <= 59:
            return f"{hh:02d}:{mm:02d}"
    m = re.match(r"^(\d{1,2})$", s)
    if m:
        hh = int(m.group(1))
        if 0 <= hh <= 23:
            return f"{hh:02d}:00"
    return None


def step_hours(stdscr, current_time: str) -> tuple[str, str] | None:
    options = [
        (f"Now → 18:00", f"Start at {current_time}, stop at 18:00"),
        (f"Now → 14:00", f"Start at {current_time}, half day"),
        (f"Now → 20:00", f"Start at {current_time}, long day"),
        ("Other",        "I'll specify"),
    ]
    cursor = 0
    error  = ""

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        draw_frame(stdscr, 2, 3, "When are you working today?")
        if error:
            stdscr.attron(curses.color_pair(PAIR_ERROR))
            stdscr.addnstr(4, 2, error, w - 2)
            stdscr.attroff(curses.color_pair(PAIR_ERROR))
            draw_options(stdscr, options, cursor, start_row=5)
        else:
            draw_options(stdscr, options, cursor)
        stdscr.refresh()

        key = stdscr.getch()
        if key in (ord("q"), ord("Q"), 27):
            return None
        elif key == curses.KEY_UP:
            cursor = max(0, cursor - 1)
        elif key == curses.KEY_DOWN:
            cursor = min(len(options) - 1, cursor + 1)
        elif key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
            if cursor == 0:
                return (current_time, "18:00")
            elif cursor == 1:
                return (current_time, "14:00")
            elif cursor == 2:
                return (current_time, "20:00")
            else:
                # Custom time input
                stdscr.erase()
                draw_frame(stdscr, 2, 3, "When are you working today?")
                stdscr.addnstr(5, 2, "Start time:", w - 2)
                start_s = get_text_input(stdscr, 5, 14, 8)
                if start_s is None:
                    continue
                start_t = parse_time(start_s)
                if not start_t:
                    error = f"Invalid: '{start_s}' — use HH:MM or H"
                    continue
                stdscr.addnstr(7, 2, "End time:  ", w - 2)
                end_s = get_text_input(stdscr, 7, 14, 8)
                if end_s is None:
                    continue
                end_t = parse_time(end_s)
                if not end_t:
                    error = f"Invalid: '{end_s}' — use HH:MM or H"
                    continue
                return (start_t, end_t)


DURATION_CHOICES = ["15m", "30m", "1h", "2h", "3h+", "Other"]


def pick_duration(stdscr, block_desc: str) -> str | None:
    """Sub-step: pick duration for a block. Returns duration string or None."""
    cursor = 0
    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        draw_frame(stdscr, 3, 3, f"Duration: {block_desc}")
        opts = [(d, "") for d in DURATION_CHOICES]
        draw_options(stdscr, opts, cursor)
        stdscr.refresh()

        key = stdscr.getch()
        if key in (ord("q"), ord("Q"), 27):
            return None
        elif key == curses.KEY_UP:
            cursor = max(0, cursor - 1)
        elif key == curses.KEY_DOWN:
            cursor = min(len(DURATION_CHOICES) - 1, cursor + 1)
        elif key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
            chosen = DURATION_CHOICES[cursor]
            if chosen != "Other":
                return chosen
            # Custom duration
            stdscr.erase()
            draw_frame(stdscr, 3, 3, f"Duration: {block_desc}")
            stdscr.addnstr(5, 2, "Duration (e.g. 45m, 1h30m):", w - 2)
            custom = get_text_input(stdscr, 5, 30, 10)
            return custom if custom else None


def step_blocks(stdscr) -> list[dict]:
    blocks: list[dict] = []
    cursor = 0

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        draw_frame(stdscr, 3, 3, "Anything with a fixed time today?")

        # Show existing blocks
        body_start = 5
        if blocks:
            stdscr.attron(curses.color_pair(PAIR_ADDED))
            for j, b in enumerate(blocks):
                stdscr.addnstr(body_start + j, 4,
                               f"• {b['description']} — {b['duration']}", w - 4)
            stdscr.attroff(curses.color_pair(PAIR_ADDED))
            body_start += len(blocks) + 1

        options: list[tuple[str, str]] = [("None — nothing scheduled", "")]
        if blocks:
            options = [
                ("+ Add another block", ""),
                ("Done", "Confirm and continue"),
            ]
        else:
            options = [
                ("None — nothing scheduled", ""),
                ("+ Add a block", "Meeting, call, errand — include duration"),
            ]

        draw_options(stdscr, options, cursor, start_row=body_start)
        stdscr.refresh()

        key = stdscr.getch()
        if key in (ord("q"), ord("Q"), 27):
            return blocks
        elif key == curses.KEY_UP:
            cursor = max(0, cursor - 1)
        elif key == curses.KEY_DOWN:
            cursor = min(len(options) - 1, cursor + 1)
        elif key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
            label = options[cursor][0]
            if label.startswith("None") or label == "Done":
                return blocks
            elif label.startswith("+ Add"):
                # Get description
                stdscr.erase()
                draw_frame(stdscr, 3, 3, "Add a scheduled block")
                stdscr.addnstr(5, 2, "What is it? (e.g. 'Team standup')", w - 2)
                desc = get_text_input(stdscr, 6, 4, w - 6)
                if not desc:
                    continue
                dur = pick_duration(stdscr, desc)
                if dur:
                    blocks.append({"description": desc, "duration": dur})
                cursor = 0  # reset after adding


# ── Main ──────────────────────────────────────────────────────────────────────

def run(stdscr, current_time: str) -> dict | None:
    curses.curs_set(0)
    setup_colors()

    energy = step_energy(stdscr)
    if energy is None:
        return None

    hours = step_hours(stdscr, current_time)
    if hours is None:
        return None
    start_time, end_time = hours

    blocks = step_blocks(stdscr)

    return {
        "energy":           energy,
        "start_time":       start_time,
        "end_time":         end_time,
        "scheduled_blocks": blocks,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--working-date",  required=True)
    parser.add_argument("--current-time",  required=True, help="HH:MM wall-clock")
    args = parser.parse_args()

    tty_fd    = os.open("/dev/tty", os.O_RDWR)
    old_stdin = os.dup(0)
    os.dup2(tty_fd, 0)
    os.close(tty_fd)
    try:
        result = curses.wrapper(lambda scr: run(scr, args.current_time))
    finally:
        os.dup2(old_stdin, 0)
        os.close(old_stdin)

    if result is None:
        sys.exit(1)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
