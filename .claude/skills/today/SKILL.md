---
name: today
description: Generate daily plan from due tasks and active projects, bounded by the morning check-in. Re-runnable throughout the day.
---

# /today - Daily Plan

Generate or refresh today's plan. Reads the morning check-in from the daily file and builds a time-bounded, energy-gated task list.

**Prerequisite:** `/today-start` must have been run first. If the daily file has no `## Morning Check-in` section, tell the operator to run `/today-start` and stop.

---

## Step 1 — Read daily file and check-in

```bash
bash .claude/hooks/get-datetime.sh full
```

Read `_documentation/_agenda/daily/YYYY-MM-DD.md`.

Extract from it:
- `energy-ceiling` from frontmatter
- Scheduled blocks and their durations from `## Morning Check-in`
- Anchored tasks (commitments) from `## Morning Check-in`
- Available time from `## Time Budget`

If the file doesn't exist or has no check-in, respond:

> No morning check-in found. Run `/today-start` first.

And stop.

---

## Step 2 — Gather tasks

1. **Find tasks by due date using grep** (never glob all tasks):
   ```bash
   # Today's tasks (pending or in-progress only)
   grep -rl "due: YYYY-MM-DD" _documentation/_agenda/tasks/ 2>/dev/null
   
   # All pending/in-progress tasks for overdue check
   grep -rl "status: pending\|status: in-progress" _documentation/_agenda/tasks/ 2>/dev/null
   ```
   Then filter overdue by comparing due dates against today.

2. Read only the matching task files. Extract: `priority`, `energy`, `duration`.

3. Grep `_documentation/_agenda/projects/*.md` for `status: active`, read those files for next actions.

4. Check what's been done today:
   ```bash
   git log --since="midnight" --grep="cos:" --oneline
   ```

---

## Step 3 — Build the plan

### Ordering rules

1. **Anchored tasks first** — the 1–3 commitments from the check-in. These get the first slots.
2. **Due today** — remaining tasks due today, sorted by priority within energy tier.
3. **Overdue** — carried forward, flagged with days overdue.
4. **Active projects** — next action from each active project (only if time remains).

### Energy gating

Apply the energy ceiling from the check-in:

- **Ceiling: low** → move all `energy: high` and `energy: medium` tasks to `## Deferred (energy)`.
- **Ceiling: medium** → allow `energy: high` tasks only before midday; any that would land after midday go to `## Deferred (energy)`.
- **Ceiling: high** → no gating.

### Time gating

Sum all task durations (anchored + due + overdue). Compare against available time.

If total exceeds available time, show clearly:

```
⚠ Overloaded: Planned Xh Ym | Available Xh Ym | Over by Xh Ym
```

Do NOT silently drop tasks. Present the full list and ask:

> This day is overloaded by [amount]. What should we defer or move to tomorrow?

Wait for the operator to decide before writing.

---

## Step 4 — Update daily file

Write or update the following sections in `_documentation/_agenda/daily/YYYY-MM-DD.md`.

**Preserve existing sections** — `## Morning Check-in`, `## Time Budget`, `## Session Log`, `## Breaks` must not be overwritten.

Update or create these sections:

```markdown
## Due Today
- [ ] [task name] — `energy:` `duration:` `priority:` — [[tasks/slug]]

## Overdue
- [ ] [task name] — X days overdue — `energy:` `duration:` — [[tasks/slug]]

## Deferred (energy)
- [task name] — deferred: energy ceiling is [level] — [[tasks/slug]]

## Active Projects
- [Project Name] — next: [next action from file]

## Today So Far
- [items from git log since midnight]
```

### On re-run (refreshing mid-day)

When `/today` is run again later in the day:
- Recalculate remaining time: available time minus durations of completed tasks
- Keep `[x]` completed items in place
- Update `## Today So Far` with latest git log
- If new tasks were added to the vault since last run, include them
- Show updated budget: `Remaining: Xh Ym of Xh Ym`
