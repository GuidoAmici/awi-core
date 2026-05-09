---
name: today
description: Daily hub — start the day, view/refresh plan, or close out. Re-runnable throughout the day.
allowed-tools: Read, Write, Edit, Bash, Glob
model: sonnet
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

## Step 1 — Resolve working date

```bash
bash .claude/hooks/get-datetime.sh full
```

**The day starts at 6am.** The working date is the calendar date whose 6am most recently passed:
- If current hour ≥ 6:00 → working date = today
- If current hour < 6:00 → working date = yesterday

**All file paths, dates, week numbers, and git log anchors use the working date throughout every mode.**

The working week follows from the working date (week starts Monday 6am).
Git log anchor: `--since="<working-date> 06:00:00"`

---

## Step 2 — Detect state and route

Read `<agenda-base>daily/<working-date>.md` if it exists. Extract from frontmatter:
- `checked-in:` — true/false
- `checked-out:` — true/false

**Always check yesterday:** regardless of current hour, if yesterday's file exists and is not checked out, launch the open-session TUI:

```bash
python3 .claude/skills/today/scripts/open_session.py \
  --day-name <YesterdayDayName> \
  --working-date <yesterday-date>
```

Read stdout JSON: `{"action": "continue" | "close_start"}`

- `"continue"` → working date = yesterday, proceed to state detection below
- `"close_start"` → run **End mode** for yesterday (full Q&A, working date = yesterday), then switch working date to today and run **Start mode**

**Otherwise** (no open yesterday session), determine state from the working date's file:
- **Not started** — file missing OR `checked-in: false` → go directly to **Start mode**
- **In progress** — `checked-in: true`, `checked-out: false` → ask:
  ```
  question: "What do you need?"
  header: "Today"
  options:
    - label: "Check — view / refresh plan"    ← recommended
      description: "Build or refresh today's task list"
    - label: "End my day"
      description: "Day retrospective — planned vs actual, tomorrow handoff"
  ```
- **Done** — `checked-out: true` → go directly to **End mode** with note: "Day already closed — running retrospective anyway."

---

## Start mode

> Morning check-in. Runs automatically when no check-in exists for today.

**Do NOT skip questions.** The daily plan is only valid after the check-in is written.

### A0 — Enforcement gates

#### Monday gate: Mental model

If today is **Monday**:

1. Read this week's weekly file: `<agenda-base>weekly/YYYY-WNN.md`
2. Find `## Mental Model of the Week`
3. If present:

> 📖 This week's mental model: [[mental-models/<slug>]] — [reason]. Take 5 minutes to read it before diving in.

4. If missing, note it and continue.

### A1 — Run the check-in TUI (Q1–Q3)

Launch the check-in wizard for energy, hours, and scheduled blocks:

```bash
python3 .claude/skills/today/scripts/start_checkin.py \
  --working-date <working-date> \
  --current-time <HH:MM from get-datetime.sh>
```

Read stdout JSON:
```json
{
  "energy": "high" | "medium" | "low",
  "start_time": "HH:MM",
  "end_time": "HH:MM",
  "scheduled_blocks": [{"description": "...", "duration": "..."}]
}
```

If the script exits non-zero (user quit), stop and wait.

| energy value | Energy ceiling |
|---|---|
| high | high |
| medium | medium |
| low | low |

### A1.5 — Q4: What are you committing to finishing today?

Launch the task picker TUI (hard cap: 3 selections):

```bash
python3 .claude/skills/shared/scripts/today_issues.py --working-date <working-date> \
  | python3 .claude/skills/today/scripts/task_picker.py
```

Read stdout JSON array of selected issues. If empty (user quit without selecting), proceed with no anchored tasks.

These become **anchored tasks** in Check mode — scheduled first.

### A2 — Calculate time budget

Compute from Q2 answers:

```
Start time:        [HH:MM from Q2]
End time:          [HH:MM from Q2]
Working window:    end - start
Scheduled blocks:  [sum from Q3]
Available time:    working window - scheduled blocks
```

Show:

> Your day: start [HH:MM], stop [HH:MM], [Xh Ym] available after scheduled blocks.

### A3 — Write to daily file

Create or update `<agenda-base>daily/YYYY-MM-DD.md`. Preserve all existing sections.

```markdown
---
type: daily
date: YYYY-MM-DD
checked-in: true
checked-out: false
energy-ceiling: high | medium | low
start-time: "HH:MM"
end-time: "HH:MM"
---

# DayOfWeek, Month DD

## Morning Check-in
- **Feeling:** [answer] → energy ceiling: [high/medium/low]
- **Working:** [HH:MM] → [HH:MM]
- **Scheduled blocks:**
  - [block description] — [duration]
  - (or "None")
- **Committing to:**
  - [issue ref or description]

## Time Budget
| | |
|---|---|
| Start | HH:MM |
| End | HH:MM |
| Working window | Xh Ym |
| Scheduled blocks | Xh Ym |
| Available for tasks | Xh Ym |
```

After writing:

> Check-in saved. Run `/today` again to build your plan.

Log: `python3 .claude/skills/shared/scripts/log_command.py today-start completed`

---

---

## Check mode

> Builds or refreshes today's task list. Requires a check-in.

If daily file has no `## Morning Check-in` section:

> No morning check-in found. Run `/today` → "Start my day" first.

And stop.

### B1 — Run the data script and launch plan TUI

```bash
python3 .claude/skills/shared/scripts/today_issues.py --working-date <working-date>
```

Parse the JSON output. Surface any `errors` to the user before continuing.

Then pipe it to the plan TUI:

```bash
python3 .claude/skills/shared/scripts/today_issues.py --working-date <working-date> \
  | python3 .claude/skills/today/scripts/check_plan.py
```

Read stdout JSON:
```json
{
  "deferred":  [{"number": N, "source_repo": "...", "title": "...", "reason": "..."}],
  "unplanned": [{"title": "..."}],
  "refreshed": bool
}
```

Incorporate deferred and unplanned items when writing the daily file (B4).

Read anchored tasks (commitments) from `## Morning Check-in` in the daily file.

### B2 — Gather active projects

Active projects are still read from files — they are context docs, not issues.

```bash
grep -rl "status: active" <org-agenda-base>projects/ 2>/dev/null
```

Read each matching file. Extract: project name, `## Next Action` content. Keep as project context, not as scheduled tasks. Run for each active org.

**Git log:**

```bash
git log --since="<working-date> 06:00:00" --grep="cos:" --oneline
```

### B2.5 — Build convergence map

Group all gathered tasks (personal + org) into **2–5 themes** by domain/project cluster. Rules:

1. Name each theme concisely (e.g. "NewHaze DS v2", "CI/CD Infra", "AWI Tooling")
2. Count pending/in-progress items per theme
3. Identify **gate issues** — issues blocking multiple others (look for "blocked by" / "depends on" in issue body, or `priority:high` issues whose `project:` label appears in many other issues). Mark as gate.
4. Pick the top 1–2 recommended focus themes based on: gates unlocked, priority density, active momentum.

If more than 8 themes, merge the smallest into "Other".

This map is informational only — it does not change task ordering or time budget.

### B3 — Build the plan

**Ordering:**
1. Pinned issues first (manually flagged `pinned` label)
2. Anchored tasks (morning commitments) — match against issue titles if possible
3. `priority:high` open issues — sorted by energy tier
4. `priority:medium` open issues
5. `priority:low` — list only, don't schedule unless time permits
6. Active projects — next action only if time remains

**Energy gating:**
- Ceiling low → move all `energy:high` and `energy:medium` issues to `## Deferred (energy)`
- Ceiling medium → allow `energy:high` before midday only; rest deferred
- Ceiling high → no gating

**Time gating:**

Sum `duration` labels of scheduled issues. If total exceeds available time:

```
⚠ Overloaded: Planned Xh Ym | Available Xh Ym | Over by Xh Ym
```

Ask:

> This day is overloaded by [amount]. What should we defer?

Wait before writing.

**On re-run:**
- Recalculate remaining time (available minus completed issue durations)
- Keep `[x]` items in place
- Update `## Today So Far` with latest git log
- Include issues added since last run
- Show: `Remaining: Xh Ym of Xh Ym`

### B4 — Update daily file

Preserve: `## Morning Check-in`, `## Time Budget`, `## Session Log`, `## Breaks`.

Update or create:

```markdown
## Pinned
- [ ] [issue title] `[org-name]` — `energy:` `duration:` `priority:` — [org-workspace#N]

## Today's Plan
- [ ] [issue title] `[org-name]` — `energy:` `duration:` `priority:` — [org-workspace#N]
- [ ] [issue title] `[org-name]` — `energy:` `duration:` `priority:` — [org-workspace#N]

## Deferred (energy)
- [issue title] `[org-name]` — deferred: energy ceiling is [level] — [org-workspace#N]

## Active Projects
- [Project Name] `[org-name]` — next: [next action from project file]

## Convergence Map
> Cross-org snapshot — [N] pending items across [M] orgs + personal

| Theme | Tasks | Gate |
|-------|-------|------|
| [Theme name] | N | [gate task or —] |

**Focus:** [Theme X] → [reason: gate unlocked / priority / momentum]

## Today So Far
- [items from git log since last 6am]
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

## End mode

> Day retrospective. Runs automatically when day is already closed, or when chosen from the in-progress menu.

### C0 — Which day?

Use the working date resolved in Step 1 as `<target-date>` for all file reads and writes in this mode. (Before 6:00 → yesterday; 6:00 or later → today.)

### C1 — Get the full picture

Read `<agenda-base>daily/<target-date>.md`. Extract:
- `energy-ceiling` from frontmatter
- Morning commitments from `## Morning Check-in`
- Time budget from `## Time Budget`
- All `## Session Log` sections
- All `## Breaks` entries

Read current week file. Derive the ISO week number from the **working date** (not wall-clock):

```bash
date -d "<working-date>" '+%G-W%V'
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

### C6 — Friday gate: Week review

If `<target-date>` is a **Friday**:

1. Check if this week's weekly file exists: `<agenda-base>weekly/YYYY-WNN.md`
2. If it doesn't exist, or has no `## Selected for This Week` section with actual content:

> ⚠ Week review not done. Run `/week-review` before closing Friday — it sets next week's priorities.

**Block the close-out.** Do not write `checked-out: true` or log `today-end` until `/week-review` is complete.

Once `/week-review` is done, return here and finish End mode normally.

Log: `python3 .claude/skills/shared/scripts/log_command.py today-end completed`
