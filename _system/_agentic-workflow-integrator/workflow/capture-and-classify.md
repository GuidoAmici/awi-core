---
kind: workflow
---

# Capture & Classify

How raw input becomes structured vault data.

---

## Entry points

| Trigger | Use when |
|---|---|
| `/new <text>` | Quick natural-language capture during the day |
| Direct message | Describing a task, project, or situation conversationally |
| Paste / upload | Dropping in an email, screenshot, or doc to extract from |

---

## Classification rules

| What it is | Where it goes | Key signal |
|---|---|---|
| Single action with a done state | `tasks/` | Has a clear completion condition |
| Ongoing initiative with multiple tasks | `projects/` | Multiple steps, no single end state |
| User-facing offering | `products/` | A product with a name and apps |
| Individual | `people/` | A named person who matters to the work |
| Loose concept, not yet actionable | `ideas/` | No due date, no owner, not a project yet |
| Deliverable that was produced | `outputs/` | Something was built, decided, or written |

**When in doubt between task and project:** if you can write it as one checkbox, it's a task. If it needs subtasks to be meaningful, it's a project.

**When in doubt between idea and task:** if it has no due date and no owner, it's an idea. Promote it to a task when it has both.

---

## Linking on creation

When creating a file, immediately connect it:

- Task → link to its parent project: `[[projects/project-slug]]`
- Task/Project → link to product: `[[products/product-slug]]`
- Project → update its product file to include `[[projects/project-slug]]`
- Person → link from any task/project that involves them

Never create an island. Every new file should be reachable from at least one other file.

---

## Confidence scoring

Rate classification confidence 0.0–1.0 before committing:

| Score | Meaning | Action |
|---|---|---|
| 0.9+ | Clear intent | Proceed silently |
| 0.7–0.9 | Probably right | Proceed, note in commit message |
| 0.5–0.7 | Uncertain | Note in commit, flag in body |
| < 0.5 | Ambiguous | Ask before filing |

---

## Quick capture shorthand

`/new` parses natural language automatically:

```
/new call Ana about pricing proposal by Thursday
→ task: call-ana-pricing-proposal.md (due: Thursday)
→ person: ana.md (created if missing)

/new new project: migrate auth to SSO, involves backend and consumer panel
→ project: migrate-auth-sso.md (linked to relevant product/app)
```
