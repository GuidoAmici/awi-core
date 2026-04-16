---
name: today-start
description: Morning intake ritual. Asks how you're feeling, what's scheduled, and what you're committing to — writes the check-in to today's daily file.
---

# /today-start - Morning Intake

Captures the operator's state and constraints before the day begins. Run once in the morning — `/today` reads from this.

**Do NOT skip questions.** The daily plan is only valid after the check-in is written.

---

## Path Resolution

Before accessing any agenda files:

1. Read `_system/users/current-user.md`
2. Extract the `user:` field — this is `<user-root>` (e.g. `_clients/guido-amici/`)
3. `<agenda-base>` = `<user-root>agenda/`

If `current-user.md` does not exist: stop and tell the operator to run `/awi-user-login`.

---

## Step 0 — Enforcement gates

Before starting the intake, check for overdue rituals.

```bash
bash .claude/hooks/get-datetime.sh full
```

### Friday gate: Week review

If today is **Friday** (or Saturday/Sunday and no review was done):

1. Check if this week's weekly file exists: `<agenda-base>weekly/YYYY-WNN.md`
2. If it doesn't exist, or it has no `## Selected for This Week` section:

> ⚠ Weekly review hasn't been done yet. Run `/week-review` before planning today — it sets next week's priorities.

**Block the intake** until `/week-review` is complete or the operator explicitly says to skip.

### Monday gate: Mental model

If today is **Monday**:

1. Read this week's weekly file: `<agenda-base>weekly/YYYY-WNN.md`
2. Find the `## Mental Model of the Week` entry
3. If present, remind the operator:

> 📖 This week's mental model: [[mental-models/<slug>]] — [reason]. Take 5 minutes to read it before diving in.

4. If no weekly file or no mental model entry exists, note it and continue (don't block — the model is chosen during `/week-review`).

---

## Step 1 — Get date and time

Already retrieved in Step 0. Use that timestamp as the start time.

---

## Step 2 — Ask three questions

Ask **one at a time**, waiting for each answer before proceeding to the next.

### Q1: How are you feeling?

Use the `AskUserQuestion` tool with these options (do NOT ask as plain text):

```
question: "How are you feeling right now?"
header: "Energy"
options:
  - label: "Great!"
    description: "High energy — all task types available"
  - label: "Okay"
    description: "Medium energy — high-energy tasks flagged, avoid in afternoon"
  - label: "Low"
    description: "Low energy — only low/medium tasks; high-energy deferred"
```

Map to energy ceiling:

| Answer | Energy ceiling | Effect on plan |
|---|---|---|
| Great! | high | All task types available |
| Okay | medium | High-energy tasks flagged, not scheduled in afternoon |
| Low | low | Only low/medium-energy tasks; high-energy deferred |

### Q2: What's already scheduled today?

> What's already on your schedule today? Calls, meetings, errands, appointments — anything with a fixed time or that takes a block of your day. Include duration for each.

Record each block with its duration. **Wait for the operator to confirm estimates before moving on.**

If the operator says "nothing," record that.

### Q3: What are you committing to finishing today?

> What are the 1–3 things you want to finish today, no matter what?

If the operator hasn't seen the backlog yet, briefly show what's due/overdue and what's selected for this week (from the weekly file) so they can pick from real data.

These become **anchored tasks** in `/today` — scheduled first, before anything else.

---

## Step 3 — Calculate time budget

```
Start time:        [current time]
Working window:    8h (unless operator says otherwise)
Scheduled blocks:  [sum from Q2]
Available time:    working window - scheduled blocks
Recommended stop:  start time + working window
```

Show the budget to the operator:

> Your day: start [HH:MM], stop [HH:MM], [Xh Ym] available for tasks after scheduled blocks.

---

## Step 4 — Write to daily file

Read `<agenda-base>daily/YYYY-MM-DD.md` if it exists.

Create or update the file. The `## Morning Check-in` and `## Time Budget` sections go at the top, after the H1. Preserve any existing sections (`## Session Log`, `## Breaks`, etc.).

```markdown
---
type: daily
date: YYYY-MM-DD
checked-in: true
checked-out: false
energy-ceiling: high | medium | low
---

# DayOfWeek, Month DD

## Morning Check-in
- **Feeling:** [answer] → energy ceiling: [high/medium/low]
- **Scheduled blocks:**
  - [block description] — [duration]
  - (or "None")
- **Committing to:**
  - [item 1]
  - [item 2]
  - [item 3]

## Time Budget
| | |
|---|---|
| Start | HH:MM |
| Working window | 8h |
| Scheduled blocks | Xh Ym |
| Available for tasks | Xh Ym |
| **Recommended stop** | **HH:MM** |
```

After writing, tell the operator:

> Check-in saved. Run `/today` to generate your plan.

---

## Logging

At the end of this skill — regardless of outcome — log the invocation:

```bash
python3 .claude/skills/shared/scripts/log_command.py today-start <outcome>
```

`<outcome>`: `completed` | `skipped` | `errored`
