---
name: wrap
description: End-of-session ritual. Saves observations about the user and flags any unsaved info from the conversation.
allowed-tools: Read, Write, Edit, Bash, Glob
model: sonnet
subagent_type: general-purpose
---

# /wrap - End of Session

Two things before closing:
1. **Observations** — behavioral patterns noticed about the user this session
2. **Unsaved info** — anything mentioned in conversation that wasn't filed to the vault

---

## Step 1 — Observations about the user

Review the full conversation for patterns the user may not be consciously aware of:
- How they communicate (verbosity, delegation style, trust)
- How they make decisions (data-driven, intuitive, socially influenced)
- What they avoid, assume, or don't notice
- Patterns in what they asked for vs what they actually needed
- Anything surprising about how they think or work

Write 1–3 observations. Each must be:
- **Specific to this session** — grounded in what actually happened
- **Non-judgmental** — framed as observation, not evaluation
- About something they likely don't consciously track about themselves

**Before writing**, read existing entries so you don't repeat:
```bash
powershell -Command "Get-ChildItem 'D:/GitHub/GuidoAmici/second-brain/info/organization/user-profile-inference/' | Sort-Object LastWriteTime -Descending | Select-Object -First 3 -ExpandProperty FullName | ForEach-Object { Get-Content $_ -Raw }"
```

Get today's date:
```bash
powershell -Command "Get-Date -Format 'yyyy-MM-dd'"
```

Save to `info/organization/user-profile-inference/YYYY-MM-DD - Guido Amici.md`:
- If the file already exists for today: append under a new `## YYYY-MM-DD` section (don't overwrite)
- If new: create with `# Guido Amici` as H1, `## YYYY-MM-DD` as section heading

Each observation uses collapsible format:
```markdown
<details><summary><strong>Short label</strong></summary>

One short paragraph. Specific, grounded in what happened this session.

</details>
```

**Tell the user the observations out loud** — don't just silently write them.

---

## Step 2 — Unsaved info sweep

Scan the conversation for anything **mentioned but not filed**:
- Tasks or to-dos referenced but never `/new`'d
- Ideas or decisions that belong in the vault
- Project status changes not yet reflected in files
- People or meetings mentioned in passing
- Outputs (plans, designs, decisions) that should be in `info/organization/outputs/`

For each item found: name it and ask whether to file it now or skip.

If nothing unsaved: say so in one line.

---

## Output format

```
## Session observations
[observations, told out loud]

## Unsaved info
[list of items, or "Nothing detected."]
```
