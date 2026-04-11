# Commands & Skills Reference

## Quick Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `/login-second-brain <username>` | Load user profile for session | `/login-second-brain guido` |
| `/new <text>` | Quick capture — classify and file | `/new call John about project by Friday` |
| `/today` | Generate daily plan from due tasks | `/today` |
| `/week` | Weekly plan with task scheduling | `/week` |
| `/quarter` | Quarterly goals and milestones | `/quarter` |
| `/year` | Annual strategic plan | `/year` |
| `/daily-review` | End of day — planned vs actual | `/daily-review` |
| `/history` | Recent git activity | `/history` |
| `/delegate <task>` | Fork terminal for autonomous work | `/delegate write the quarterly report` |
| `/wrap-session` | End-of-session ritual | `/wrap-session` |

---

## `/new` — Quick Capture

Parses natural language, classifies entities, creates linked files.

**Input:** "New project with John Smith for marketing outbound, need landing page"

**Creates:**
- `people/john-smith.md` (if doesn't exist)
- `projects/marketing-outbound.md` (linked to John Smith)
- `tasks/create-landing-page.md` (linked to project)

---

## `/today` — Daily Planning

Generates `_documents/organization/daily/YYYY-MM-DD.md` with:

- **Due Today** — Tasks with today's due date
- **Overdue** — Past-due tasks with days overdue
- **Active Projects** — Projects with `status: active` and their next actions
- **Recent Activity** — Today's `cos:` commits

---

## `/daily-review` — End of Day

Compares planned vs actual:

1. Reads daily plan
2. Gets activity from `git log --since="8am" --grep="cos:"`
3. Updates task statuses
4. Appends review section with completed/incomplete items

---

## `/week` — Weekly Plan

Generates weekly note from due tasks, active projects, and recent activity.

---

## `/history` — Recent Activity

Shows last 7 days of Chief of Staff activity:

```bash
git log --since="7 days ago" --grep="cos:" --format="%ad %s" --date=short
```

---

## `/delegate` — Task Delegation

Forks terminal for autonomous work. See `delegation.md` for full setup.

---

## `/login-second-brain` — Load User Profile

Loads person profile from `_documents/organization/people/`. See `_documents/chief-of-staff/references/classification.md` for routing rules.

---

## `/wrap-session` — End of Session

Four-step ritual:
1. Session summary
2. Daily file update (completed + added work, impulse check)
3. Observations → `user-profile-inference/` or `people/GuidoAmici.md`
4. Unsaved info sweep
