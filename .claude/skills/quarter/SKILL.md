---
name: quarter
description: Generate quarterly plan with goals, project milestones, and task roadmap. Part of chief-of-staff vault system.
model: sonnet
subagent_type: Product Manager
---

# /quarter - Quarterly Planning

Generate a plan for the current quarter from vault contents.

## Steps

1. Get current date and determine the quarter (Q1=Jan-Mar, Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec)
2. Check if `info/organization/planning/YYYY-QN.md` exists - if so, **do not overwrite** (skip unless user explicitly asks)
3. **Gather all active/paused projects** — grep `info/organization/projects/*.md` for `status: active` and `status: paused`, read them
4. **Gather all pending/in-progress tasks** — grep `info/organization/tasks/*.md` for `status: pending` or `status: in-progress`, read them
5. **Group tasks by due month** — tasks due within the quarter grouped by month; tasks due before quarter start → Overdue
6. **Map projects to monthly milestones** — based on project next actions and linked tasks, suggest which month each project should hit its next milestone
7. **Identify undated tasks** — distribute across months by priority (same priority order as /week)
8. **Derive quarter goals** — synthesize 3-5 high-level goals from the projects and tasks. Goals should be outcome-oriented ("Launch auth across all apps") not activity-oriented ("Work on auth")
9. Run `git log --since="<quarter start>" --grep="cos:" --format="%ad %s" --date=short` for quarter activity so far
10. Create `info/organization/planning/YYYY-QN.md`

## Goal Derivation

Goals come from clustering related projects and tasks:
1. Group projects/tasks by shared tags
2. For each cluster, write one outcome-oriented goal
3. List the projects and key tasks that contribute to each goal
4. If a project doesn't fit a goal, it becomes its own goal
5. Max 5 goals — if more, merge the smallest clusters

## Monthly Milestone Mapping

For each active project, determine a monthly target:
- **Month 1**: Projects with overdue tasks or blocking other work
- **Month 2**: Projects with tasks due this quarter but not urgent
- **Month 3**: Projects with no hard deadlines, or stretch goals
- Paused projects: list under "Parking Lot" unless user has signaled intent to resume

## Update Behavior

When the quarterly file already exists:
- **Do not regenerate** unless user explicitly asks to update/refresh
- If updating: keep completed items, user edits, and custom sections
- Add new projects/tasks that appeared since last generation
- Refresh the Activity section

## Output Format

```markdown
---
type: quarterly
quarter: YYYY-QN
date-range: YYYY-MM-DD to YYYY-MM-DD
---

# QN YYYY

## Goals
1. **Goal name** — outcome description
   - Project: [[project-slug]] (next: action)
   - Task: [[task-slug]] (due: date)

## Month 1 (Month Name)
### Projects
- Project Name — milestone target for this month
### Tasks
- [ ] Task (due: date)
- [ ] Task (scheduled)

## Month 2 (Month Name)
### Projects
- Project Name — milestone target
### Tasks
- [ ] Task (due: date)

## Month 3 (Month Name)
### Projects
- Project Name — milestone target
### Tasks
- [ ] Task (due: date)

## Parking Lot
- Paused projects not planned for this quarter

## Activity So Far
- Summary of cos: commits grouped by week
```
