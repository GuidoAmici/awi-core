---
name: year
description: Generate yearly plan with strategic goals, quarterly targets, and project roadmap. Part of chief-of-staff vault system.
model: sonnet
subagent_type: Studio Producer
---

# /year - Yearly Planning

Generate a high-level plan for the year from vault contents and user input.

## Steps

1. Get current date and year
2. Check if `_workspace/guido-amici/agenda/planning/YYYY-annual.md` exists - if so, **do not overwrite** (skip unless user explicitly asks)
3. **Gather all projects** — read all `_workspace/guido-amici/agenda/projects/*.md` regardless of status
4. **Gather all tasks** — grep for `status: pending` or `status: in-progress` in `_workspace/guido-amici/agenda/tasks/*.md`
5. **Review completed work** — grep for `status: complete` in tasks and projects to understand momentum
6. **Cluster into themes** — group projects and tasks by domain tags into 3-5 strategic themes
7. **Map themes to quarters** — assign each theme a primary quarter based on dependencies and urgency
8. **Derive yearly goals** — 3-5 high-level goals that are measurable and outcome-oriented
9. **Identify dependencies** — which goals/projects block others? Note the critical path
10. **Ask user for input** — present draft goals and ask if anything is missing or needs reprioritizing
11. Create `_workspace/guido-amici/agenda/planning/YYYY-annual.md`

## Theme Clustering

Themes are broader than quarter goals — they represent strategic directions:
1. Scan all project and task tags
2. Group by domain: e.g., "auth + backend" → "Platform Infrastructure", "learn + content" → "Education Product"
3. Each theme should have 2-4 projects under it
4. Standalone projects become their own theme if significant enough

## Quarterly Mapping

Assign themes to quarters based on:
- **Q1**: Foundation work, blockers, infrastructure
- **Q2**: Core features, main product development
- **Q3**: Growth features, scaling, optimization
- **Q4**: Polish, new initiatives, next-year preparation
- Adjust based on actual project urgency and dependencies

## Dependency Tracking

For each goal, identify:
- **Blocks**: what this goal enables (downstream)
- **Blocked by**: what must complete first (upstream)
- **Critical path**: the sequence of goals that determines the earliest completion date

## Update Behavior

When the yearly file already exists:
- **Do not regenerate** unless user explicitly asks to update/refresh
- If updating: keep completed items, user edits, and custom sections
- Re-evaluate quarterly mapping based on current progress

## Output Format

```markdown
---
type: annual
year: YYYY
---

# YYYY Annual Plan

## Vision
One-paragraph description of what success looks like by end of year.

## Goals
1. **Goal name** — measurable outcome
   - Key projects: [[project-1]], [[project-2]]
   - Target quarter: QN
   - Blocked by: (dependencies)

## Q1 (Jan-Mar)
### Theme: Theme Name
- [[project-slug]] — quarterly milestone
- [[project-slug]] — quarterly milestone
### Key deliverables
- Deliverable 1
- Deliverable 2

## Q2 (Apr-Jun)
### Theme: Theme Name
...

## Q3 (Jul-Sep)
### Theme: Theme Name
...

## Q4 (Oct-Dec)
### Theme: Theme Name
...

## Parking Lot
- Projects/ideas not planned for this year but worth tracking

## Review Cadence
- Monthly: check quarterly progress against milestones
- Quarterly: run /quarter, adjust yearly plan if needed
```
