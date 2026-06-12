---
name: wrap-session
description: End-of-session ritual. Saves observations about the user and flags any unsaved info from the conversation.
allowed-tools: Read, Write, Edit, Bash, Glob, AskUserQuestion
model: sonnet
subagent_type: general-purpose
---

# /wrap-session — End of Session

Four steps, in strict order. Steps 1–3 are fully automatic — no prompts, no confirmations. Step 4 uses `AskUserQuestion`, not free-form text. Do not print progress during Step 1 — output comes in Step 2.

---

## Step 1 — Save all files silently

Save every file below without asking for confirmation. Do not pause between saves.

### 1a — Resolve context

```bash
bash .claude/hooks/get-datetime.sh full
gh api user --jq '{id: .id, login: .login, name: .name}'
```

Read `_data/users/current-user.json` to get `<user-root>`.

### 1b — Infer which orgs were touched

An org was touched if any of the following are true:
1. Files were edited under `_data/organizations/<name>/`
2. Issues were referenced by an org workspace repo (e.g. `GuidoAmici/newhaze-workspace`, `GuidoAmici/rabbitek-workspace`)

The org name is the repo prefix before `-workspace` (e.g. `newhaze` from `GuidoAmici/newhaze-workspace`). Build a list of touched org names — use it for Steps 1d and 1e.

### 1c — User inference file

Path: `<user-root>agenda/user-profile-inference/YYYY-MM-DD-<login>.md`

Review the conversation for behavioral patterns the user may not be consciously aware of:
- How they communicate (verbosity, delegation style, trust)
- How they make decisions (data-driven, intuitive, socially influenced)
- What they avoid, assume, or don't notice
- Patterns in what they asked for vs what they actually needed

Write 1–3 observations. Each must be:
- **Specific to this session** — grounded in what actually happened
- **Non-judgmental** — framed as observation, not evaluation
- About something they likely don't consciously track
- **Must include explicit Pros and Cons**

Before writing, check existing entries to avoid repetition:
```bash
ls <user-root>agenda/user-profile-inference/ | sort -r | head -3
```

Format:
```markdown
<details><summary><strong>Short label</strong></summary>

One short paragraph. Specific, grounded in what happened this session.

**Pros:** What this pattern enables or where it serves the user well.
**Cons:** Where this pattern may create friction, blind spots, or tradeoffs.

</details>
```

- If the file exists for today: append a new `<details>` block
- If new: create with `# <name>` as H1, `## YYYY-MM-DD` as section heading

### 1d — User daily file

Path: `<user-root>agenda/daily/YYYY-MM-DD.md`

If it doesn't exist, create it:
```markdown
---
type: daily
date: YYYY-MM-DD
checked-in: false
checked-out: false
---

# DayOfWeek, Month DD
```

Append a `## Session Log` section with:

**Completed this session** — everything done, marked `[x]`, linked to task file if one exists. Include unscheduled work.

**Added this session** — every task, decision, or idea created this session. For each: priority (`critical` / `high` / `medium` / `low`) and a flag: **[strategic]** or **[reactive]**.

**Impulse check** — one line: was this session mostly strategic or reactive? If reactive dominated, name it plainly.

### 1e — Org daily files

For each org touched, save `_data/organizations/<name>/agenda/daily/YYYY-MM-DD.md`.

If it doesn't exist, create with minimal structure:
```markdown
---
type: daily
org: <name>
date: YYYY-MM-DD
---

# DayOfWeek, Month DD — <name>
```

Append a `## Session Log` section summarising work done for that org this session.

### 1f — Outputs files

If any outputs were produced during the session (plans, designs, decisions, reports), save them to:
- `<user-root>agenda/outputs/YYYY-MM-DD-<slug>.md` for personal outputs
- `_data/organizations/<name>/agenda/outputs/YYYY-MM-DD-<slug>.md` for org-specific outputs

Only create outputs files for content that was actually produced, not for the session log itself.

---

## Step 2 — Print one-liner per file saved

After all saves, print a single line per file:

```
_data/users/42481462/agenda/user-profile-inference/2026-05-14-GuidoAmici.md — 2 observations added
_data/users/42481462/agenda/daily/2026-05-14.md — session log appended
_data/organizations/newhaze/agenda/daily/2026-05-14.md — created, session log added
_data/users/42481462/agenda/outputs/2026-05-14-wrap-session-rewrite.md — created
```

---

## Step 3 — Session summary

Print 3–6 bullet points covering actions taken and open threads. Focus on outcomes, not process.

```
## Session summary
- [action or outcome]
- [action or outcome]
- ...
```

---

## Step 4 — Unsaved info gate

Scan the conversation for anything mentioned but not filed:
- Tasks or to-dos referenced but never created
- Ideas or decisions that belong in the vault
- Project status changes not yet reflected in files
- People or meetings mentioned in passing

For each unsaved item, use `AskUserQuestion` with one question at a time. Do not dump a markdown list. Do not use free-form text. One call per item, wait for a response before asking the next.

If nothing is unsaved, say so in one line and stop.

---

## Logging

```bash
python3 .claude/skills/shared/scripts/log_command.py wrap-session <outcome>
```

`<outcome>`: `completed` | `skipped` | `errored`
