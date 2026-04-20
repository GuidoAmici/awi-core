---
name: week-review
description: Friday ritual. Review all pending tasks, re-rank by priority, and select next week's work batch.
---

# /week-review - Weekly Priority Review

Run every Friday. Reviews the full backlog, re-ranks by priority, and selects next week's work.

**This is the scheduling engine.** Daily plans pull from what this review selects.

---

## Path Resolution

Before accessing any agenda files:

1. Read `_data/users/current-user.md`
2. Extract the `user:` field — this is `<user-root>` (e.g. `_data/users/42481462/`)
3. `<agenda-base>` = `<user-root>agenda/`

If `current-user.md` does not exist: stop and tell the operator to run `/awi-user`.

---

## Step 1 — Gather the full picture

```bash
bash .claude/hooks/get-datetime.sh full
```

1. **All pending/in-progress tasks:**
   ```bash
   grep -rl "status: pending\|status: in-progress" <agenda-base>tasks/ 2>/dev/null
   ```
   Read each. Extract: `priority`, `energy`, `duration`, `due`, `product`, `feature`.

2. **Active projects:**
   ```bash
   grep -rl "status: active" <agenda-base>projects/ 2>/dev/null
   ```
   Read each for next actions.

3. **This week's daily files** — scan for patterns: what got done, what got deferred, what kept slipping.

4. **Approaching deadlines** — any task with `due:` within the next 14 days.

---

## Step 2 — Present the backlog

Show the operator a ranked table:

```
| # | Task | Priority | Energy | Duration | Due | Product |
|---|------|----------|--------|----------|-----|---------|
```

Sort by:
1. Priority (critical → high → medium → low)
2. Within same priority: approaching deadline first
3. Within same priority + no deadline: by product grouping

Flag any tasks that have been pending for more than 2 weeks without progress.

---

## Step 3 — Operator selects next week's batch

Ask:

> Here's the full backlog ranked by priority. Which items are you taking on next week? You can pick by number, add items, or adjust priorities.

The operator picks. For each selected item, confirm or adjust:
- Priority (still accurate?)
- Energy level (still accurate?)
- Duration estimate (still accurate?)
- Due date (needs one? needs updating?)

---

## Step 4 — Write weekly file

Create `<agenda-base>weekly/YYYY-WNN.md`:

```markdown
---
type: weekly
week: YYYY-WNN
---

# Week NN, YYYY

## Mental Model of the Week
[[mental-models/<slug>]] — [one-line reason this model is relevant to this week's work]

## Selected for This Week
| Task | Priority | Energy | Duration | Due |
|------|----------|--------|----------|-----|
| [[tasks/slug]] | high | medium | 1h | Apr 10 |

**Total estimated time:** Xh Ym
**Available time (5 days × ~Xh):** ~XXh

## Backlog (not selected)
- [remaining tasks, briefly listed]

## Carried Over
- [items selected last week that didn't get done — flag why]

## Active Projects — Status
- [project] — [current state, next action]
```

---

## Step 5 — Mental model selection

Choose a mental model from `<agenda-base>ideas/mental-models/` that is **relevant to this week's selected work**, not random.

To choose:
1. Read `<agenda-base>ideas/mental-models/_index.md` for the full list
2. Look at the selected tasks and active projects for the week
3. Pick the model that best applies to the dominant theme (e.g., negotiation week → "incentives"; refactoring week → "first-principles"; overloaded week → "opportunity-cost")
4. Write a one-line justification in the weekly file

---

## Step 6 — Confirm

Show the operator the weekly plan and ask:

> This is next week. Realistic? Anything to adjust?

Only write after confirmation.

---

## Logging

At the end of this skill — regardless of outcome — log the invocation:

```bash
python3 .claude/skills/shared/scripts/log_command.py week-review <outcome>
```

`<outcome>`: `completed` | `skipped` | `errored`
