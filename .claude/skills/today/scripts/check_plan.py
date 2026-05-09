#!/usr/bin/env python3
"""
check_plan.py — Plan view TUI for /today Check mode.

Reads today_issues.py JSON from stdin. Displays plan with interactive actions.
Outputs JSON to stdout on exit.

Usage:
    python3 .claude/skills/shared/scripts/today_issues.py \
        | python3 .claude/skills/today/scripts/check_plan.py

Output:
    {
        "deferred":  [{"number": N, "source_repo": "...", "title": "...", "reason": "..."}],
        "unplanned": [{"title": "..."}],
        "refreshed": bool
    }
"""
import curses
import json
import os
import subprocess
import sys
import webbrowser

# ── Colour pairs ──────────────────────────────────────────────────────────────
PAIR_HEADER   = 1
PAIR_CURSOR   = 2
PAIR_DIM      = 3
PAIR_FOOTER   = 4
PAIR_SECTION  = 5
PAIR_PINNED   = 6
PAIR_DEFERRED = 7
PAIR_UNPLANNED = 8
PAIR_INPUT    = 9
PAIR_STATUS   = 10
PAIR_HIGH     = 11

ENERGY_RANK   = {"high": 0, "medium": 1, "low": 2}
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


def setup_colors() -> None:
    curses.start_color()
    curses.use_default_colors()
    bg = -1
    curses.init_pair(PAIR_HEADER,    curses.COLOR_BLACK,  curses.COLOR_CYAN)
    curses.init_pair(PAIR_CURSOR,    curses.COLOR_BLACK,  curses.COLOR_WHITE)
    curses.init_pair(PAIR_DIM,       curses.COLOR_WHITE,  bg)
    curses.init_pair(PAIR_FOOTER,    curses.COLOR_WHITE,  bg)
    curses.init_pair(PAIR_SECTION,   curses.COLOR_CYAN,   bg)
    curses.init_pair(PAIR_PINNED,    curses.COLOR_YELLOW, bg)
    curses.init_pair(PAIR_DEFERRED,  curses.COLOR_RED,    bg)
    curses.init_pair(PAIR_UNPLANNED, curses.COLOR_GREEN,  bg)
    curses.init_pair(PAIR_INPUT,     curses.COLOR_YELLOW, bg)
    curses.init_pair(PAIR_STATUS,    curses.COLOR_CYAN,   bg)
    curses.init_pair(PAIR_HIGH,      curses.COLOR_RED,    bg)


def energy_allowed(issue_energy: str, ceiling: str | None) -> bool:
    """True if issue energy is within the ceiling (lower demand = allowed)."""
    if ceiling is None:
        return True
    return ENERGY_RANK.get(issue_energy, 1) >= ENERGY_RANK.get(ceiling, 0)


def build_plan(data: dict) -> tuple[list, list, list]:
    ceiling = data.get("energy_ceiling")
    pinned  = data.get("pinned", [])
    issues  = data.get("issues", [])

    plan, deferred = [], []
    for issue in issues:
        if energy_allowed(issue.get("energy", "medium"), ceiling):
            plan.append(issue)
        else:
            deferred.append(issue)

    plan.sort(key=lambda i: (
        PRIORITY_RANK.get(i.get("priority", "medium"), 1),
        ENERGY_RANK.get(i.get("energy", "medium"), 1),
    ))
    return pinned, plan, deferred


def fmt_line(issue: dict, w: int, prefix: str = "  ") -> str:
    meta_parts = []
    org = issue.get("org")
    if org:
        meta_parts.append(org)
    if issue.get("priority") == "high":
        meta_parts.append("!")
    dur = issue.get("duration")
    if dur:
        meta_parts.append(dur)
    meta   = "  ".join(meta_parts)
    meta_w = min(len(meta) + 2, w // 3)
    title_w = max(1, w - len(prefix) - meta_w - 1)
    title  = issue.get("title", "")[:title_w]
    return f"{prefix}{title:<{title_w}} {meta:>{meta_w}}"


def get_text_input(stdscr, row: int, col: int, width: int,
                   prompt: str = "") -> str | None:
    h, w = stdscr.getmaxyx()
    if prompt:
        stdscr.addnstr(row, col, prompt, max(0, w - col))
        col = min(col + len(prompt), w - 2)
    curses.curs_set(1)
    buf: list[str] = []

    while True:
        field   = "".join(buf)
        display = field[-width:] if len(field) >= width else field
        avail   = min(width, max(0, w - col))
        if avail > 0:
            stdscr.attron(curses.color_pair(PAIR_INPUT) | curses.A_UNDERLINE)
            stdscr.addnstr(row, col, display.ljust(avail)[:avail], avail)
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


# ── Nav item type aliases ─────────────────────────────────────────────────────
# Each nav entry: (kind, payload)
# kind: "section" | "pinned" | "plan" | "deferred_energy" | "deferred_user" | "unplanned"

class PlanView:
    def __init__(self, data: dict) -> None:
        self.data   = data
        self.pinned, self.plan, self.deferred_energy = build_plan(data)
        self.deferred_user: list[dict]  = []
        self.unplanned:     list[dict]  = []
        self.refreshed = False
        self.cursor = 0
        self.scroll  = 0
        self.status  = ""
        self._rebuild()

    def _rebuild(self) -> None:
        nav: list[tuple[str, object]] = []
        if self.pinned:
            nav.append(("section", "PINNED"))
            nav.extend(("pinned", i) for i in self.pinned)
        if self.plan:
            nav.append(("section", "TODAY'S PLAN"))
            nav.extend(("plan", i) for i in self.plan)
        if self.unplanned:
            nav.append(("section", "UNPLANNED"))
            nav.extend(("unplanned", i) for i in self.unplanned)
        ceiling = self.data.get("energy_ceiling")
        if self.deferred_energy:
            nav.append(("section",
                        f"DEFERRED — energy ceiling: {ceiling or '?'}"))
            nav.extend(("deferred_energy", i) for i in self.deferred_energy)
        if self.deferred_user:
            nav.append(("section", "DEFERRED — by you"))
            nav.extend(("deferred_user", i) for i in self.deferred_user)
        self.nav = nav
        self.cursor = max(0, min(self.cursor, len(self.nav) - 1))
        self._skip_sections()

    def _skip_sections(self) -> None:
        """Ensure cursor is never on a section header."""
        if not self.nav:
            return
        while self.cursor < len(self.nav) and self.nav[self.cursor][0] == "section":
            self.cursor += 1
        if self.cursor >= len(self.nav):
            self.cursor = len(self.nav) - 1
            while self.cursor > 0 and self.nav[self.cursor][0] == "section":
                self.cursor -= 1

    def _current_issue(self) -> tuple[str, dict] | tuple[None, None]:
        if 0 <= self.cursor < len(self.nav):
            kind, item = self.nav[self.cursor]
            if kind in ("pinned", "plan", "deferred_energy", "deferred_user"):
                return kind, item
        return None, None

    def _issue_key(self, issue: dict) -> tuple:
        return (issue.get("source_repo", ""), issue.get("number", -1))

    def defer_current(self, reason: str) -> bool:
        kind, issue = self._current_issue()
        if issue and kind in ("pinned", "plan"):
            entry = {**issue, "reason": reason}
            self.deferred_user.append(entry)
            key = self._issue_key(issue)
            if kind == "pinned":
                self.pinned = [i for i in self.pinned
                               if self._issue_key(i) != key]
            else:
                self.plan = [i for i in self.plan
                             if self._issue_key(i) != key]
            self._rebuild()
            return True
        return False

    def add_unplanned(self, title: str) -> None:
        self.unplanned.append({"title": title})
        self._rebuild()

    def issue_url(self, issue: dict) -> str | None:
        repo   = issue.get("source_repo")
        number = issue.get("number")
        if repo and number:
            return f"https://github.com/{repo}/issues/{number}"
        return None

    def refresh(self) -> str:
        try:
            result = subprocess.run(
                ["python3", ".claude/skills/shared/scripts/today_issues.py"],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode != 0:
                return f"Refresh failed: {result.stderr.strip()[:50]}"
            new_data = json.loads(result.stdout)
            deferred_keys = {self._issue_key(d) for d in self.deferred_user}
            self.data = new_data
            self.pinned, self.plan, self.deferred_energy = build_plan(new_data)
            self.pinned = [i for i in self.pinned
                           if self._issue_key(i) not in deferred_keys]
            self.plan   = [i for i in self.plan
                           if self._issue_key(i) not in deferred_keys]
            self.refreshed = True
            self._rebuild()
            return "Refreshed"
        except Exception as e:
            return f"Refresh error: {str(e)[:50]}"

    def draw(self, stdscr) -> None:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        # Header
        avail = self.data.get("available_minutes")
        if avail is not None and avail >= 0:
            rem = f"{avail // 60}h {avail % 60:02d}m"
            right = f" Remaining: {rem} "
        else:
            right = ""
        hdr_left = " /today — Today's Plan"
        stdscr.attron(curses.color_pair(PAIR_HEADER) | curses.A_BOLD)
        stdscr.addnstr(0, 0, hdr_left.ljust(max(0, w - len(right))),
                       max(0, w - len(right)))
        if right:
            stdscr.addnstr(0, max(0, w - len(right)), right, len(right))
        stdscr.attroff(curses.color_pair(PAIR_HEADER) | curses.A_BOLD)

        stdscr.attron(curses.color_pair(PAIR_DIM))
        stdscr.addnstr(1, 0, "─" * w, w)
        stdscr.attroff(curses.color_pair(PAIR_DIM))

        # List
        list_start = 2
        list_end   = h - 3
        list_rows  = max(1, list_end - list_start)

        if self.cursor < self.scroll:
            self.scroll = self.cursor
        elif self.cursor >= self.scroll + list_rows:
            self.scroll = self.cursor - list_rows + 1

        for i, (kind, item) in enumerate(
                self.nav[self.scroll: self.scroll + list_rows]):
            row     = list_start + i
            abs_idx = self.scroll + i
            is_cur  = abs_idx == self.cursor

            if kind == "section":
                stdscr.attron(curses.color_pair(PAIR_SECTION) | curses.A_BOLD)
                stdscr.addnstr(row, 0, f"  {item}", w)
                stdscr.attroff(curses.color_pair(PAIR_SECTION) | curses.A_BOLD)

            elif kind == "pinned":
                prefix = "> ★ " if is_cur else "  ★ "
                line   = fmt_line(item, w, prefix)
                attr   = (curses.color_pair(PAIR_CURSOR) | curses.A_BOLD
                          if is_cur else curses.color_pair(PAIR_PINNED))
                stdscr.attron(attr)
                stdscr.addnstr(row, 0, line.ljust(w), w)
                stdscr.attroff(attr)

            elif kind == "plan":
                prefix = "> " if is_cur else "  "
                line   = fmt_line(item, w, prefix)
                attr   = (curses.color_pair(PAIR_CURSOR) | curses.A_BOLD
                          if is_cur else curses.A_NORMAL)
                stdscr.attron(attr)
                stdscr.addnstr(row, 0, line.ljust(w), w)
                stdscr.attroff(attr)

            elif kind == "unplanned":
                prefix = "> " if is_cur else "  "
                line   = f"{prefix}[+] {item.get('title', '')}"
                attr   = (curses.color_pair(PAIR_CURSOR) | curses.A_BOLD
                          if is_cur else curses.color_pair(PAIR_UNPLANNED))
                stdscr.attron(attr)
                stdscr.addnstr(row, 0, line[:w].ljust(w), w)
                stdscr.attroff(attr)

            elif kind in ("deferred_energy", "deferred_user"):
                prefix = "> " if is_cur else "  "
                reason = item.get("reason", "")
                if reason:
                    title_w = max(1, w - len(prefix) - len(reason) - 5)
                    line = f"{prefix}[~] {item.get('title','')[:title_w]}  · {reason}"
                else:
                    line = fmt_line(item, w, f"{prefix}[~] ")
                attr = (curses.color_pair(PAIR_CURSOR) | curses.A_BOLD
                        if is_cur else curses.color_pair(PAIR_DEFERRED))
                stdscr.attron(attr)
                stdscr.addnstr(row, 0, line[:w].ljust(w), w)
                stdscr.attroff(attr)

        # Footer
        stdscr.attron(curses.color_pair(PAIR_DIM))
        stdscr.addnstr(h - 3, 0, "─" * w, w)
        stdscr.attroff(curses.color_pair(PAIR_DIM))

        if self.status:
            stdscr.attron(curses.color_pair(PAIR_STATUS))
            stdscr.addnstr(h - 2, 0, f" {self.status}".ljust(w), w)
            stdscr.attroff(curses.color_pair(PAIR_STATUS))
        else:
            keys = " ↑↓ move   D defer   A add   O open   R refresh   Q done"
            stdscr.attron(curses.color_pair(PAIR_FOOTER))
            stdscr.addnstr(h - 2, 0, keys.ljust(w), w)
            stdscr.attroff(curses.color_pair(PAIR_FOOTER))

        stdscr.refresh()


def run(stdscr, data: dict) -> dict:
    curses.curs_set(0)
    setup_colors()

    view = PlanView(data)

    while True:
        view.draw(stdscr)
        view.status = ""
        h, w = stdscr.getmaxyx()

        key = stdscr.getch()

        if key in (ord("q"), ord("Q"), 27):
            break

        elif key == curses.KEY_UP:
            view.cursor = max(0, view.cursor - 1)
            while view.cursor > 0 and view.nav[view.cursor][0] == "section":
                view.cursor -= 1

        elif key == curses.KEY_DOWN:
            view.cursor = min(len(view.nav) - 1, view.cursor + 1)
            while (view.cursor < len(view.nav) - 1
                   and view.nav[view.cursor][0] == "section"):
                view.cursor += 1

        elif key == curses.KEY_PPAGE:
            view.cursor = max(0, view.cursor - 10)
            view._skip_sections()

        elif key == curses.KEY_NPAGE:
            view.cursor = min(len(view.nav) - 1, view.cursor + 10)
            view._skip_sections()

        elif key in (ord("d"), ord("D")):
            kind, issue = view._current_issue()
            if issue and kind in ("pinned", "plan"):
                view.draw(stdscr)
                reason = get_text_input(stdscr, h - 2, 0, w - 1, " Defer reason: ")
                if reason:
                    title = issue.get("title", "")
                    view.defer_current(reason)
                    view.status = f"Deferred: {title[:45]}"
            else:
                view.status = "Move cursor to a plan item first"

        elif key in (ord("a"), ord("A")):
            view.draw(stdscr)
            title = get_text_input(stdscr, h - 2, 0, w - 1, " Unplanned task: ")
            if title:
                view.add_unplanned(title)
                view.status = f"Added: {title[:50]}"

        elif key in (ord("o"), ord("O")):
            kind, issue = view._current_issue()
            if issue:
                url = view.issue_url(issue)
                if url:
                    try:
                        webbrowser.open(url)
                        view.status = f"Opened in browser"
                    except Exception:
                        view.status = "Could not open browser"
            else:
                view.status = "Move cursor to an issue first"

        elif key in (ord("r"), ord("R")):
            view.status = "Refreshing…"
            view.draw(stdscr)
            view.status = view.refresh()

    return {
        "deferred":  view.deferred_user,
        "unplanned": view.unplanned,
        "refreshed": view.refreshed,
    }


def main() -> None:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"check_plan: invalid JSON: {e}\n")
        sys.exit(1)

    if data.get("state") == "needs_checkin":
        sys.stderr.write("check_plan: no check-in yet — run Start mode first\n")
        sys.exit(1)

    tty_fd    = os.open("/dev/tty", os.O_RDWR)
    old_stdin = os.dup(0)
    os.dup2(tty_fd, 0)
    os.close(tty_fd)
    try:
        result = curses.wrapper(lambda scr: run(scr, data))
    finally:
        os.dup2(old_stdin, 0)
        os.close(old_stdin)

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
