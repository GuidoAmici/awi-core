---
kind: workflow
---

# GTD — Task Selection

How to choose what to work on next. GTD defines four criteria, applied in order.

---

## The four criteria

| # | Criterion | Question |
|---|---|---|
| 1 | **Context** | Can I do this here, with the tools I have? |
| 2 | **Time available** | Do I have enough time to start and finish (or reach a clean stopping point)? |
| 3 | **Energy available** | Does my current mental and physical state match what this task demands? |
| 4 | **Priority** | Of everything that passes the first three filters, which matters most? |

Most systems skip to priority. GTD doesn't — because doing a high-priority task at the wrong energy level produces worse results than doing a medium-priority task well.

---

## Energy levels

Tasks carry an `energy:` field in their frontmatter:

| Level | What it requires | Best time of day |
|---|---|---|
| `high` | Deep focus — complex thinking, decisions, architecture, writing | Morning (peak) |
| `medium` | Standard engagement — calls, reviews, research, execution | Midday |
| `low` | Mechanical — admin, filing, replies, simple updates | Late afternoon / end of day |

The daily plan (`/today`) groups tasks by energy tier so the schedule matches the natural curve of a working day.

---

## How this maps to the vault

- **Context** → handled implicitly by where you are (not tracked as a field — physical/digital context is assumed)
- **Time available** → `duration:` on every task + scheduled blocks declared in morning intake. `/today` sums durations against available time and flags overload before the day starts
- **Energy available** → `energy: high | medium | low` on every task
- **Priority** → `priority: critical | high | medium | low` on every task

When choosing what to do, filter first by energy match, then sort by priority within that tier.

---

## Scheduling rule

When generating a daily plan:

1. High-energy tasks → schedule in the first work block
2. Medium-energy tasks → midday block
3. Low-energy tasks → end of day, or fill gaps between focused blocks
4. If a high-priority task has `energy: high` but it's already late in the day, flag it rather than silently move it — the operator decides whether to push or force it

---

## Source

David Allen, *Getting Things Done* (2001). The four-criteria model is in Chapter 9: "The 'Do' Phase: Making the Best Action Choices."
