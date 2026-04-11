---
name: break
description: Log a break to today's daily file. Tracks start/end times and motive so /wrap-session can calculate actual work time.
---

# /break - Log a Break

Logs break time to today's daily file. Used to track actual working time vs planned time.

---

## Usage

- `/break <motive>` — start a break (logs current time + reason)
- `/break back` — end a break (logs current time as break end, shows duration)

---

## How it works

Get the current time:
```bash
bash .claude/hooks/get-datetime.sh time
```

Read `_documentation/_agenda/daily/YYYY-MM-DD.md`.

If the file doesn't exist, say:

> No daily file for today. Run `/today-start` first.

### Starting a break (`/break <motive>`)

Append to the `## Breaks` section:

```markdown
- **HH:MM** — [motive] — started
```

Tell the operator:

> Break started at HH:MM. Say `/break back` when you're back.

### Ending a break (`/break back`)

Find the last `started` entry in `## Breaks` that has no end time. Calculate duration.

Update the line:

```markdown
- **HH:MM – HH:MM** — [motive] — Xm
```

Calculate running totals and tell the operator:

> Back at HH:MM. Break was Xm. Total breaks today: Xh Ym. Remaining work time: Xh Ym.

---

## Running totals

When ending a break, always show:

```
Break:              Xm ([motive])
Total breaks today: Xh Ym
Remaining work time: Xh Ym
```

Read the `## Time Budget` section to calculate remaining work time = available - breaks taken.
