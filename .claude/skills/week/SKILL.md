---
name: week
description: Generate weekly plan from due tasks, active projects, and recent activity. Part of chief-of-staff vault system.
model: sonnet
subagent_type: Sprint Prioritizer
---

# /week - Weekly Planning

Two modes:
- **`/week`** — read and display the current week's plan from `info/organization/weekly/YYYY-WNN.md`. If the file doesn't exist, say so and suggest running `/week:new`.
- **`/week:new`** — create a new weekly plan or update/overwrite the existing one from vault contents.

---

## /week — Display mode

1. Get current date, determine ISO week number
2. Read `info/organization/weekly/YYYY-WNN.md` and display it
3. Done — no file writes

---

## /week:new — Generate/update mode

### Steps

1. Get current date and determine the **target week** (current week if Mon-Thu, next week if Fri-Sun)
2. Determine the ISO week number and Mon-Sun range for the target week
3. Check if `info/organization/weekly/YYYY-WNN.md` exists — if updating, preserve `[x]` completed items
4. **Find tasks by due date using grep** (never glob all tasks):
   - Grep for `due: YYYY-MM-DD` for each day of the target week (Mon-Sun)
   - Grep for dates before Monday → Overdue
   - Only grep tasks with `status: pending` or `status: in-progress` (exclude complete/cancelled)
5. Read only the matching task files
6. **Schedule undated tasks**: find pending/in-progress tasks with no `due:` date, read them, and distribute across the week by priority:
   - Higher priority tags first: `infrastructure` > `backend` > `frontend` > `feature` > `devops`
   - Spread evenly across weekdays (Mon-Fri), heavier days early in the week
   - Mark these as "(scheduled)" in the plan to distinguish from hard due dates
7. Grep `info/organization/projects/*.md` for `status: active`, read those files
8. **Fill empty days with project work**: if any weekday has no tasks after steps 4-6, suggest continuing with an active or paused project. Priority order: `infrastructure` > `backend` > `frontend` > `feature` > `devops` > other (based on project tags). Mark these as "(project)" in the plan. Include the project's next action.
9. Run `git log --since="last monday" --grep="cos:" --oneline` for recent activity
10. Group tasks by day of the week
11. Create `info/weekly/YYYY-WNN.md`

## Task Discovery (grep-first approach)

All tasks have `due: YYYY-MM-DD` in frontmatter. Use grep to find relevant tasks efficiently:

```bash
# This week's tasks (replace with actual date range)
grep -rl "due: 2026-03-0[2-8]" info/organization/tasks/*.md

# Overdue: dates before this Monday
grep -rl "due: 2026-0[12]" info/organization/tasks/*.md  # adjust pattern for range

# Filter out completed/cancelled
grep -L "status: complete" <files> | xargs grep -L "status: cancelled"
```

Only read files returned by grep. Never glob and read all task files.

## Scheduling Undated Tasks

```bash
# Find tasks with no due date
grep -rL "due:" info/organization/tasks/*.md | xargs grep -l "status: pending\|status: in-progress"
```

Read each undated task. Assign to weekdays (Mon-Fri) by priority:
1. Read tags to determine priority (infra > backend > frontend > feature > devops > other)
2. Fill Monday first, then Tuesday, etc. — max 3 tasks per day
3. Mark with "(scheduled)" so user knows these are suggestions, not hard deadlines

## Filling Empty Days with Projects

If after scheduling dated and undated tasks there are still empty weekdays, suggest project work:

1. Grep `info/organization/projects/*.md` for `status: active` first, then `status: paused` as fallback
2. Read matching projects, sort by tag priority (infra > backend > frontend > feature > devops > other)
3. Assign the highest-priority project's next action to the first empty day, second-highest to the next, etc.
4. Mark with "(project)" so user knows these are project continuations, not standalone tasks
5. If multiple empty days remain after all projects are assigned, repeat the highest-priority project

## Update Behavior

When the weekly file already exists:
- **Do not regenerate** unless user explicitly asks to update/refresh
- If updating: keep `[x]` completed items, manually added items, and custom sections
- Add new tasks from vault that aren't already present
- Refresh the Activity section with latest git log

## Mental Model of the Week

Every weekly plan includes one mental model to study and apply during the week.

**Rotation:** use `(ISO week number - 1) mod 20` to pick from this ordered list:

0. first-principles
1. inversion
2. occams-razor
3. map-territory
4. second-order-thinking
5. confirmation-bias
6. hanlons-razor
7. loss-aversion
8. dunning-kruger
9. availability-heuristic
10. feedback-loops
11. leverage
12. emergence
13. compounding
14. bottleneck
15. opportunity-cost
16. incentives
17. sunk-cost-fallacy
18. margin-of-safety
19. supply-demand

Read `info/organization/ideas/mental-models/<slug>.md` to get the model's name and core question.

Include this section **immediately after the `# Week NN, YYYY` heading**, before any tasks:

```markdown
## Mental Model of the Week
**[[mental-models/<slug>]]** — *<core question>*
- [ ] Monday: Read the note
- [ ] Before Sunday: Log one real application in a daily note (tag: `#mental-model`)
```

---

## Output Format

```markdown
---
type: weekly
week: YYYY-WNN
date-range: YYYY-MM-DD to YYYY-MM-DD
---

# Week NN, YYYY

## Mental Model of the Week
**[[mental-models/<slug>]]** — *<core question>*
- [ ] Monday: Read the note
- [ ] Before Sunday: Log one real application in a daily note (tag: `#mental-model`)

## Overdue
- [ ] Task (due: YYYY-MM-DD, X days overdue)

## Monday (MM-DD)
- [ ] Task items due this day

## Tuesday (MM-DD)
- [ ] Task items due this day

## Wednesday (MM-DD)
- [ ] Task items due this day

## Thursday (MM-DD)
- [ ] Task items due this day

## Friday (MM-DD)
- [ ] Task items due this day

## Weekend (MM-DD - MM-DD)
- [ ] Task items due Sat/Sun

## Active Projects
- Project Name (next: next action from file)

## Activity So Far
- Items from git log grouped by day
```
