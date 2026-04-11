# File Formats

All files use YAML frontmatter with markdown body.

All files live under `_documents/organization/` subfolders.

## Task

```markdown
---
type: task
due: YYYY-MM-DD
status: pending | in-progress | complete | cancelled
priority: critical | high | medium | low
product: product-slug
app: app-slug  # if applicable
feature: feature-slug  # if applicable
tags: [tag1, tag2]
created: YYYY-MM-DDTHH:MM:SS
---

# Task Title

Description of what needs to be done.

## Notes
- Additional context
- Related information
```

**Status values:**
- `pending` - Not started
- `in-progress` - Currently working on
- `complete` - Done
- `cancelled` - No longer needed

**Priority values:**
- `critical` - Blocking or time-sensitive — address immediately, today if possible
- `high` - Must happen this week/sprint — do not delay
- `medium` - Should happen this sprint, can slip one week
- `low` - Nice to have, freely deferrable to a later sprint

## Project

```markdown
---
type: project
status: active | paused | complete | archived
product: product-slug
app: app-slug  # if applicable
tags: [tag1, tag2]
created: YYYY-MM-DD
---

# Project Name

Brief description of the project.

## Next Action
Single most important next step.

## Notes
- Key dates
- Stakeholders
- Context
```

## Product

```markdown
---
type: product
status: active | paused | archived
tags: [category]
---

# Product Name

Brief description of the product.

## Apps
- [[app-slug]] — description

## Notes
- Business context
- Key stakeholders
```

## Person

```markdown
---
type: person
tags: [relationship-type]
last-contact: YYYY-MM-DD
---

# Person Name

Role/relationship description.

## Roles
- What they do

## Preferences
- Self-stated working preferences (dated)

## Long-term patterns
- Observed behavioral patterns (graduated from user-profile-inference)

## Follow-ups
- Pending items with this person
```

## Idea

```markdown
---
type: idea
tags: [category]
created: YYYY-MM-DDTHH:MM:SS
---

# Idea Title

The idea description.

## Related
- Links to related projects/tasks
```

## Output

```markdown
---
type: output
date: YYYY-MM-DD
tags: [tag1, tag2]
affects:
  - wiki/arquitectura-digital/stack  # wiki files updated as a result of this decision
---

# Output Title

## What changed

## Why

## Trade-offs
```

**`affects` field:**
- List every wiki file whose content was updated as a result of this output.
- Use paths relative to `_documents/organization/newhaze-wiki/` without the `.md` extension.
- Leave empty (`affects: []`) only if the output is purely analytical (audit, research, UX mapping) with no permanent changes.
- If the output *should* update a wiki file but hasn't yet, list it anyway — it signals a pending sync.

## Daily Note

```markdown
---
type: daily
date: YYYY-MM-DD
---

# Day, Month DD

## Due Today
- [ ] Task items

## Overdue
- [ ] Carry-forward items (X days)

## Active Projects
- Project (next: action)

## Session Log

### Completed this session
- [x] Item — [[task-slug]]

### Added this session
- task name — `priority` — [strategic|reactive]

**Impulse check:** [one line]

## Review
(Appended at end of day)
- ✅ Completed items
- ⏳ Incomplete items
```

## Weekly Note

```markdown
---
type: weekly
week: YYYY-WNN
---

# Week NN, YYYY

## Completed
- Summary of completed tasks

## In Progress
- Ongoing work

## Planned for Next Week
- Upcoming priorities
```

## User Profile Inference

```markdown
---
type: about-you
date: YYYY-MM-DD
---

# Person Name

## YYYY-MM-DD

<details><summary><strong>Short label</strong></summary>

One short paragraph. Specific, grounded in what happened this session.

</details>
```
