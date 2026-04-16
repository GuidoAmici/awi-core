---
name: week
description: Display the current week's plan. Shows selected tasks, mental model, and progress.
---

# /week - View Weekly Plan

Display the current week's plan. Read-only — use `/week-review` to create or update.

## Path Resolution

Before accessing any agenda files:

1. Read `_system/users/current-user.md`
2. Extract the `user:` field — this is `<user-root>` (e.g. `_clients/guido-amici/`)
3. `<agenda-base>` = `<user-root>agenda/`

If `current-user.md` does not exist: stop and tell the operator to run `/awi-user-login`.

## Steps

1. Get the current date and ISO week number:
   ```bash
   bash .claude/hooks/get-datetime.sh full
   date '+%G-W%V'
   ```

2. Read `<agenda-base>weekly/YYYY-WNN.md`

3. If it doesn't exist:
   > No weekly plan found for this week. Run `/week-review` to create one.

4. If it exists, display it and add a progress summary:
   - How many selected tasks are complete vs pending
   - Any approaching deadlines (tasks with `due:` this week)
   - Mental model status: read or not applied yet

---

## Logging

At the end of this skill — regardless of outcome — log the invocation:

```bash
python3 .claude/skills/shared/scripts/log_command.py week <outcome>
```

`<outcome>`: `completed` | `skipped` | `errored`
