---
name: wrap-session
description: End-of-session ritual. Saves observations about the user and flags any unsaved info from the conversation.
allowed-tools: Read, Write, Edit, Bash, Glob
model: sonnet
subagent_type: general-purpose
---

# /wrap-session - End of Session

Five things before closing:
1. **Session summary** — what was done and where things stand
2. **Daily file update** — log completed work and tasks added on the run
3. **Observations** — behavioral patterns noticed about the user this session
4. **Unsaved info** — anything mentioned in conversation that wasn't filed to the vault
5. **Rename session** — use `/rename` to give the conversation a descriptive title

---

## Step 1 — Session summary

Briefly recap what happened this session: what was asked, what was done, and current state. Keep it short — 3–6 bullet points max. Focus on actions taken and any open threads, not on reasoning or process.

Format:
```
## Session summary
- [action or outcome]
- [action or outcome]
- ...
```

Tell this to the user out loud before moving on.

---

## Step 2 — Daily file update

Read today's daily file at `_documentation/_agenda/daily/YYYY-MM-DD.md`.

If it doesn't exist yet, skip this step and note it in the output.

Append a `## Session Log` section (or add to an existing one) with two subsections:

### Completed this session
List everything that was done, whether or not it was on the plan. Mark each with `[x]` and link the task file if one exists. Include unscheduled work — that's the point.

### Added this session
List every task, decision, or idea that was created or filed during this session. For each one, include:
- Its priority (`critical` / `high` / `medium` / `low`)
- A flag: **[strategic]** if it was clearly planned or high-value, **[reactive]** if it was triggered in the moment (tool tweaks, housekeeping, low-stakes ideas)

Then add a one-line **Impulse check**: was this session's added work mostly strategic or reactive? If reactive work dominated — especially low-priority items — name it plainly. The goal is to make the pattern visible without editorializing.

Example:
```markdown
## Session Log

### Completed this session
- [x] Added `priority` field to task format — [[file-formats]]
- [x] Backfilled priority across all 30 tasks

### Added this session
- `priority` field spec — `low` — [reactive] (arose from conversation, not planned)
- `/wrap-session` skill rename — `low` — [reactive] (tool housekeeping mid-session)

**Impulse check:** Mostly reactive. No scheduled tasks were touched.
```

---

## Step 3 — Observations and profile updates

Two distinct files serve different purposes — use the right one:

Use the logged-in user's username (from `/awi-user-login`) as `<Username>` throughout this step.

| File | What goes here |
|------|----------------|
| `user-profile-inference/YYYY-MM-DD - <Username>.md` | Patterns Claude *noticed* — things the user likely doesn't consciously track about themselves |
| `people/<Username>.md` | Profile facts, preferences, and things the user *self-stated* — dated entries |

### 3a — Unaware patterns → user-profile-inference

Review the conversation for behavioral patterns the user may not be consciously aware of:
- How they communicate (verbosity, delegation style, trust)
- How they make decisions (data-driven, intuitive, socially influenced)
- What they avoid, assume, or don't notice
- Patterns in what they asked for vs what they actually needed

Write 1–3 observations. Each must be:
- **Specific to this session** — grounded in what actually happened
- **Non-judgmental** — framed as observation, not evaluation
- About something they likely don't consciously track

Each observation must include a **pros/cons split**: what this pattern enables or serves the user well, and where it may create friction or blind spots.

**Before writing**, read existing entries so you don't repeat:
```bash
ls _documentation/_agenda/user-profile-inference/ | sort -r | head -3
```
Then read the most recent 1–2 files.

Save to `_documentation/_agenda/user-profile-inference/YYYY-MM-DD - <Username>.md`:
- If the file already exists for today: append a new `<details>` block (don't add a new `##` heading)
- If new: create with `# <Username>` as H1, `## YYYY-MM-DD` as section heading

```markdown
<details><summary><strong>Short label</strong></summary>

One short paragraph. Specific, grounded in what happened this session.

**Pros:** What this pattern enables or where it serves the user well.
**Cons:** Where this pattern may create friction, blind spots, or tradeoffs.

</details>
```

### 3b — Self-stated facts → people/<Username>.md § Preferences

If the user explicitly stated a preference, working style, or self-awareness this session, add it to `_documentation/_agenda/people/<Username>.md` under `## Preferences` with a `(YYYY-MM-DD)` date prefix.

### 3c — Pattern graduation

If a pattern from `user-profile-inference/` has now appeared across multiple sessions and can be considered stable, move it to `_documentation/_agenda/people/<Username>.md` under `## Long-term patterns`.

**Tell the user all observations and any graduations out loud** — don't just silently write them.

---

## Step 4 — Unsaved info sweep

Scan the conversation for anything **mentioned but not filed**:
- Tasks or to-dos referenced but never `/new`'d
- Ideas or decisions that belong in the vault
- Project status changes not yet reflected in files
- People or meetings mentioned in passing
- Outputs (plans, designs, decisions) that should be in `_documentation/_agenda/outputs/`

For each item found: name it and ask whether to file it now or skip.

If nothing unsaved: say so in one line.

---

---

## Step 5 — Rename session

Use `/rename` to give the conversation a short, descriptive title based on what was done. The title should reflect the main work of the session — not generic phrases like "wrap session" or today's date.

Examples: `Wiki personal GuidoAmici — agenda structure`, `Fix auth middleware — compliance rewrite`, `Newhaze learn audit v2`.

---

## Output format

```
## Session summary
- [action or outcome]
- ...

## Daily file
[confirmation that it was updated, or "No daily file for today — skipped."]

## Session observations
[observations, told out loud]

## Unsaved info
[list of items, or "Nothing detected."]
```
