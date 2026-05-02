---
name: today
description: Daily hub — start the day, view/refresh plan, or close out. Re-runnable throughout the day.
---

# /today - Daily Hub

Single entry point for all daily rituals. Detects current state and asks what you need.

---

## Path Resolution

Before accessing any agenda files:

1. Read `_data/users/current-user.json`
2. Extract the `user:` field — this is `<user-root>` (e.g. `_data/users/42481462/`)
3. `<agenda-base>` = `<user-root>agenda/`
4. Read `<user-root>active-orgs.json`. For each org where `active: true`, build an entry in `<org-agenda-bases>`:
   - `org-name` → `_data/organizations/<org-name>/agenda/`
   - If the file doesn't exist, `<org-agenda-bases>` = empty list (no orgs active).

If `current-user.json` does not exist: stop and tell the operator to run `/awi-user-login`.

---

## Step 1 — Detect state

```bash
bash .claude/hooks/get-datetime.sh full
```

Read `<agenda-base>daily/YYYY-MM-DD.md` if it exists. Extract from frontmatter:
- `checked-in:` — true/false
- `checked-out:` — true/false

Determine state:
- **Not started** — file missing OR `checked-in: false`
- **In progress** — `checked-in: true`, `checked-out: false`
- **Done** — `checked-out: true`

---

## Step 2 — Ask what you need

Use `AskUserQuestion` tool. Highlight the recommended option based on state:

```
question: "What do you need?"
header: "Today"
options:
  - label: "Start my day"
    description: "Morning check-in: energy, schedule, commitments"
  - label: "View / refresh plan"
    description: "Build or refresh today's task list"
  - label: "End my day"
    description: "Day retrospective — planned vs actual, tomorrow handoff"
```

**Recommended option by state:**
- Not started → "Start my day"
- In progress → "View / refresh plan"
- Done → "End my day" (note: day already closed, proceed anyway if chosen)

---

## Mode A — Start my day

> Runs the morning check-in. Equivalent to the former `/today-start`.

**Do NOT skip questions.** The daily plan is only valid after the check-in is written.

### A0 — Enforcement gates

#### Friday gate: Week review

If today is **Friday** (or Saturday/Sunday and no review was done):

1. Check if this week's weekly file exists: `<agenda-base>weekly/YYYY-WNN.md`
2. If it doesn't exist, or has no `## Selected for This Week` section:

> ⚠ Weekly review hasn't been done yet. Run `/week-review` before planning today — it sets next week's priorities.

Block the intake until `/week-review` is complete or the operator explicitly says to skip.

#### Monday gate: Mental model

If today is **Monday**:

1. Read this week's weekly file: `<agenda-base>weekly/YYYY-WNN.md`
2. Find `## Mental Model of the Week`
3. If present:

> 📖 This week's mental model: [[mental-models/<slug>]] — [reason]. Take 5 minutes to read it before diving in.

4. If missing, note it and continue.

### A1 — Ask three questions (one at a time)

#### Q1: How are you feeling?

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

| Answer | Energy ceiling |
|---|---|
| Great! | high |
| Okay | medium |
| Low | low |

#### Q2: What's already scheduled today?

> What's already on your schedule today? Calls, meetings, errands — anything with a fixed time or block. Include duration.

Record each block with duration. Wait for confirmation. If nothing, record that.

#### Q3: What are you committing to finishing today?

> What are the 1–3 things you want to finish today, no matter what?

If operator hasn't seen the backlog, briefly show what's due/overdue and what's selected this week so they can pick from real data.

These become **anchored tasks** in Mode B — scheduled first.

### A2 — Calculate time budget

```
Start time:        [current time]
Working window:    8h (unless operator says otherwise)
Scheduled blocks:  [sum from Q2]
Available time:    working window - scheduled blocks
Recommended stop:  start time + working window
```

Show:

> Your day: start [HH:MM], stop [HH:MM], [Xh Ym] available after scheduled blocks.

### A3 — Write to daily file

Create or update `<agenda-base>daily/YYYY-MM-DD.md`. Put `## Morning Check-in` and `## Time Budget` after the H1. Preserve all existing sections.

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

After writing:

> Check-in saved. Run `/today` again to generate your plan.

Log: `python3 .claude/skills/shared/scripts/log_command.py today-start completed`

---

## Mode B — View / refresh plan

> Builds or refreshes today's task list. Requires a morning check-in.

If daily file has no `## Morning Check-in` section:

> No morning check-in found. Run `/today` → "Start my day" first.

And stop.

### B1 — Read daily file and check-in

Extract:
- `energy-ceiling` from frontmatter
- Scheduled blocks and durations from `## Morning Check-in`
- Anchored tasks (commitments) from `## Morning Check-in`
- Available time from `## Time Budget`

### B2 — Gather tasks

**Personal (user agenda):**

```bash
# Today's tasks (pending or in-progress only)
grep -rl "due: YYYY-MM-DD" <agenda-base>tasks/ 2>/dev/null

# All pending/in-progress for overdue check
grep -rl "status: pending\|status: in-progress" <agenda-base>tasks/ 2>/dev/null
```

Filter overdue by comparing due dates against today. Read matching files. Extract: `priority`, `energy`, `duration`.

Grep `<agenda-base>projects/*.md` for `status: active`, read for next actions.

**Org tasks (cross-org scan):**

For each entry in `<org-agenda-bases>`, scan tasks/ and projects/ if the directory exists. Skip silently if missing.

```bash
# repeat for each active org — substitute <org-agenda-base> and <org-name>
grep -rl "status: pending\|status: in-progress\|status: active" <org-agenda-base>tasks/ 2>/dev/null
grep -rl "status: active" <org-agenda-base>projects/ 2>/dev/null
```

For each matching file extract: name (filename slug or `title:` frontmatter), `status`, `priority`. Keep org label attached as `[<org-name>]`.

```bash
git log --since="midnight" --grep="cos:" --oneline
```

### B2.5 — Build convergence map

Group all gathered tasks (personal + org) into **2–5 themes** by domain/project cluster. Rules:

1. Name each theme concisely (e.g. "NewHaze DS v2", "CI/CD Infra", "AWI Tooling")
2. Count pending/in-progress items per theme
3. Identify **gate tasks** — tasks that are explicitly blocking multiple others (look for `blocks:` frontmatter, or tasks many others depend on). Mark as gate.
4. Pick the top 1–2 recommended focus themes based on: gates unlocked, priority density, active momentum.

If more than 8 themes, merge the smallest into "Other".

This map is informational only — it does not change task ordering or time budget.

### B3 — Build the plan

**Ordering:**
1. Anchored tasks first
2. Due today — sorted by priority within energy tier
3. Overdue — flagged with days overdue
4. Active projects — next action only if time remains

**Energy gating:**
- Ceiling low → move all `energy: high` and `energy: medium` to `## Deferred (energy)`
- Ceiling medium → allow `energy: high` before midday only; rest deferred
- Ceiling high → no gating

**Time gating:**

If total duration exceeds available time:

```
⚠ Overloaded: Planned Xh Ym | Available Xh Ym | Over by Xh Ym
```

Ask:

> This day is overloaded by [amount]. What should we defer or move to tomorrow?

Wait before writing.

**On re-run:**
- Recalculate remaining time (available minus completed task durations)
- Keep `[x]` items in place
- Update `## Today So Far` with latest git log
- Include tasks added since last run
- Show: `Remaining: Xh Ym of Xh Ym`

### B4 — Update daily file

Preserve: `## Morning Check-in`, `## Time Budget`, `## Session Log`, `## Breaks`.

Update or create:

```markdown
## Due Today
- [ ] [task name] `[personal]` — `energy:` `duration:` `priority:` — [[tasks/slug]]
- [ ] [task name] `[org-name]` — `energy:` `duration:` `priority:` — [[tasks/slug]]

## Overdue
- [ ] [task name] `[personal]` — X days overdue — `energy:` `duration:` — [[tasks/slug]]
- [ ] [task name] `[org-name]` — X days overdue — `energy:` `duration:` — [[tasks/slug]]

## Deferred (energy)
- [task name] `[org-name]` — deferred: energy ceiling is [level] — [[tasks/slug]]

## Active Projects
- [Project Name] — next: [next action from file]

## Convergence Map
> Cross-org snapshot — [N] pending items across [M] orgs + personal

| Theme | Tasks | Gate |
|-------|-------|------|
| [Theme name] | N | [gate task or —] |

**Focus:** [Theme X] → [reason: gate unlocked / priority / momentum]

## Today So Far
- [items from git log since midnight]
```

After writing user daily, write org daily files:

For each org in `<org-agenda-bases>` that has at least one task appearing (checked `[x]` or unchecked `[ ]`) in the user's plan, create or update `<org-agenda-base>daily/YYYY-MM-DD.md`:

```markdown
---
type: org-daily
date: YYYY-MM-DD
org: <org-name>
---

# <Org Display Name> — DayOfWeek, Month DD

## Work Log
- **User:** <display name from current-user.json>
- **Tasks in scope:** [task name], [task name], ...
- **Completed:** [task name], ... (or "None")

## Session Log
- [items from git log since midnight filtered to this org's paths]
```

If `<org-agenda-base>daily/` does not exist, create it. Skip orgs with no tasks in today's plan.

Log: `python3 .claude/skills/shared/scripts/log_command.py today completed`

---

## Mode C — End my day

> Day retrospective. Equivalent to the former `/today-end`.

### C0 — Which day? (midnight rule)

If current hour is between 0:00 and 5:59, ask:

```
question: "Which day are you closing?"
header: "Closing day"
options:
  - label: "Yesterday (YYYY-MM-DD)"
  - label: "Today (YYYY-MM-DD)"
```

Use the selected date as `<target-date>` for all file reads and writes in this mode.
If hour is 6:00 or later, `<target-date>` = today's date. No question needed.

### C1 — Get the full picture

Read `<agenda-base>daily/<target-date>.md`. Extract:
- `energy-ceiling` from frontmatter
- Morning commitments from `## Morning Check-in`
- Time budget from `## Time Budget`
- All `## Session Log` sections
- All `## Breaks` entries

Read current week file:

```bash
date '+%G-W%V'
```

Read `<agenda-base>weekly/YYYY-WNN.md`. If it doesn't exist, create with minimal structure before continuing:

```markdown
---
type: weekly
week: YYYY-WNN
status: no-review
---

# Week NN — Month D–D, YYYY

> No `/week-review` was run this week. File created retroactively by `/today` on YYYY-MM-DD.

## Selected for This Week

*(No tasks formally selected — week-review not run.)*

## Week Pulse
```

Populate `## Week Pulse` from daily session logs.

### C2 — Ask two questions (one at a time)

**Q1:** How did today feel? Energy held up, dropped, or never arrived? Any frustration, momentum, or surprise?

**Q2:** What went as planned today? What didn't — and why?

### C3 — Build the retrospective

#### Planned vs actual
- `[x]` committed and done
- `[ ]` committed and skipped (include why if known)
- `[+]` unplanned but done

#### Deviation analysis
If reactive work dominated or committed tasks were skipped — name it plainly. No moralizing.

#### Energy read
Cross-reference answer with actual. Did breaks correlate with energy drops? Did gating hold?

#### Week pulse
> **Week so far:** [N of M selected tasks done] — [on track / behind / ahead]. [One sentence on risk or momentum.]

#### Tomorrow handoff
> **Tomorrow, start with:**
> 1. [task] — because [reason]
> 2. [task] — because [reason]

### C4 — Write to daily file

Append `## Day Review` to `<agenda-base>daily/<target-date>.md`. Update `checked-out: false` → `checked-out: true` in frontmatter.

```markdown
## Day Review

### Planned vs Actual
- [x] [commitment] — done
- [ ] [commitment] — skipped ([reason if known])
- [+] [unplanned work] — reactive

### Deviations
[One short paragraph.]

### Energy
[One sentence.]

### Week pulse
[N of M selected tasks done] — [on track / behind / ahead]. [One sentence.]

### Tomorrow
1. [task or thread]
2. [task or thread]
```

Tell the user the full retrospective out loud before writing.

### C5 — Write org daily files

For each org that had tasks in today's plan (same trigger as B4), update `<org-agenda-base>daily/<target-date>.md`:

- Set `## Work Log` → `Completed:` based on `[x]` items from user daily
- Append `## Session Summary`:

```markdown
## Session Summary
### Planned vs Actual
- [x] [org task] — done
- [ ] [org task] — skipped ([reason if known])

### Notes
[One sentence — what moved, what didn't, handoff if relevant.]
```

Create `<org-agenda-base>daily/` directory if it doesn't exist.

Log: `python3 .claude/skills/shared/scripts/log_command.py today-end completed`
