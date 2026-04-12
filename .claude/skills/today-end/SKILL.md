---
name: today-end
description: End-of-day ritual. Reviews the full day — deviations from plan, what didn't get done, energy and frustrations, what worked vs didn't, and where to pick up tomorrow. Gives a brief read on how the week is tracking.
allowed-tools: Read, Write, Edit, Bash, Glob
model: sonnet
---

# /today-end - End of Day Review

Run once at the end of the day. This is a day-level retrospective — not a session log (that's `/wrap-session`) but a read on the whole day as a unit.

---

## Step 1 — Get the full picture

```bash
bash .claude/hooks/get-datetime.sh full
```

Read today's daily file at `_documentation/_agenda/daily/YYYY-MM-DD.md`. Extract:
- `energy-ceiling` from frontmatter
- Morning commitments from `## Morning Check-in`
- Time budget from `## Time Budget`
- All `## Session Log` sections (there may be multiple if sessions were branched)
- All `## Breaks` entries

Also read the current week file:
```bash
date '+%G-W%V'
```
Read `_documentation/_agenda/weekly/YYYY-WNN.md` for what was selected this week.

---

## Step 2 — Ask the user two questions (one at a time)

### Q1: Energy and tone

> How did today feel? Energy held up, dropped, or never arrived? Any frustration, momentum, or surprise?

Wait for the answer. Don't prompt further — just listen.

### Q2: What worked and what didn't

> What went as planned today? What didn't — and why?

Wait for the answer.

---

## Step 3 — Build the retrospective

Synthesize what you know (daily file + session logs + breaks) with what the user just said. Produce a structured read:

### Planned vs actual

Compare morning commitments against session log completions:
- What was committed to and got done — `[x] done`
- What was committed to and didn't get done — `[ ] skipped` (include why if known)
- What got done that wasn't planned — `[+] unplanned`

### Deviation analysis

If there were significant deviations (reactive work dominated, or committed tasks were skipped), name the pattern plainly. Don't moralize — just describe what happened and what it cost.

### Energy read

Cross-reference the user's answer with what actually happened:
- Did breaks correlate with energy drops?
- Did high-energy tasks get done when energy was high, or did energy-gating break down?
- Note if the morning energy ceiling (`high/medium/low`) matched reality.

### Week pulse

Look at the weekly file. How many selected tasks have been done vs pending? Is the week on track, behind, or ahead?

Output a one-liner:

> **Week so far:** [N of M selected tasks done] — [on track / behind / ahead]. [One sentence on risk if behind, or momentum if ahead.]

---

## Step 4 — Where to pick up tomorrow

Based on what didn't get done today and the week's remaining selected tasks, identify the 1–2 highest-priority items to start tomorrow with. Don't generate a full plan — just a clear handoff:

> **Tomorrow, start with:**
> 1. [task or thread] — because [reason: overdue / blocking / high energy required]
> 2. [task or thread] — because [reason]

---

## Step 5 — Append to daily file

Append a `## Day Review` section to `_documentation/_agenda/daily/YYYY-MM-DD.md`. Preserve all existing sections.

Also update `checked-out: false` → `checked-out: true` in the frontmatter.

```markdown
## Day Review

### Planned vs Actual
- [x] [commitment] — done
- [ ] [commitment] — skipped ([reason if known])
- [+] [unplanned work] — reactive

### Deviations
[One short paragraph. What pattern dominated today and what it cost, if anything.]

### Energy
[One sentence on how energy actually went vs the morning ceiling.]

### Week pulse
[N of M selected tasks done] — [on track / behind / ahead]. [One sentence.]

### Tomorrow
1. [task or thread]
2. [task or thread]
```

---

## Output format

Tell the user the full retrospective out loud before writing to the file. Keep it concise — the goal is a clear read, not a long report.
