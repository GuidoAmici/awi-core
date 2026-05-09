# Reality Check Report — /today skill tasks
**Date:** 2026-04-29  
**Agent:** TestingRealityChecker  
**Methodology:** Specification Reality Check — gap claims verified against SKILL.md line numbers. Default verdict: NEEDS WORK.

---

## Source Files Read

| File | Purpose |
|---|---|
| `.claude/skills/today/SKILL.md` | Authoritative current implementation (397 lines) |
| `agenda/tasks/today-skill-multi-org.md` | Task 1 |
| `agenda/tasks/today-commitments-multiselect.md` | Task 2 |
| `_data/users/42481462/active-orgs.json` | Actual format of active-orgs file |

---

## Task 1 — `/today skill — multi-org support`

**Verdict: NEEDS WORK**  
*Gaps are real. Solution direction is sound. Spec has ambiguity gaps that will cause implementation drift.*

### Gap Verification

All four problem claims verified against SKILL.md:

| Claim | Evidence | Status |
|---|---|---|
| "Ignores all org tasks" | B2 (lines 208–213): greps only `<agenda-base>tasks/` | ✅ CONFIRMED |
| "Never writes to org daily files" | A3 (lines 146–184), B4 (lines 259–281): writes only `<agenda-base>daily/YYYY-MM-DD.md` | ✅ CONFIRMED |
| "Ignores active-orgs.json entirely" | Path Resolution (lines 12–21): reads only `current-user.md` | ✅ CONFIRMED |
| "Silently loses org-level work attribution" | No org tagging anywhere in B2–B4 output | ✅ CONFIRMED |

Actual `active-orgs.json` format (verified at `_data/users/42481462/active-orgs.json`):
```json
{ "newhaze": { "active": true }, "rabbitek": { "active": true }, "afin": { "active": true } }
```
Task spec says "for each org where `active: true`" — format matches, field reference is correct.

### Solution Clarity Issues

**Ambiguity 1 — "had session work" trigger (A3/B4)**  
> "For each org that has tasks appearing in today's plan OR had session work"

"Session work" is undefined. Git log? Which commit pattern? The git log query in B2 (line 221) uses `--grep="cos:"` — is org work attributed to org via commit message pattern? This is not specified. An implementer would guess.

**Ambiguity 2 — Org daily file format**  
Task says "Org daily records: which user worked, what org tasks were in scope, session log from git." No template provided. The user daily template is fully specified (lines 148–178). Org daily has zero format spec. Implementer invents it → divergence guaranteed.

**Ambiguity 3 — B4 output format with mixed sources**  
Task says tag tasks `[personal]` or `[<org-name>]`. SKILL.md B4 template (lines 264–279) has no column for source tags. No updated template showing where these labels appear. Does `## Due Today` become a flat list with inline tags? Or split by org into sections? Unspecified.

**Ambiguity 4 — Missing org `agenda/tasks/` directory**  
No fallback behavior specified if `_data/organizations/<org>/agenda/tasks/` doesn't exist (e.g. org just created). Silent skip? Error? The task says "Orgs with no tasks due today are skipped silently" — only covers empty results, not missing directory.

### Acceptance Criteria Assessment

| Criterion | Testable? | Issue |
|---|---|---|
| newhaze tasks surface in "View / refresh plan" | ✅ Yes | None |
| Completing newhaze work creates/updates org daily | ✅ Yes | Depends on "session work" definition — currently undefined |
| `active-orgs.json` drives inclusion — toggle removes from plan | ✅ Yes | None |
| Orgs with no tasks skipped silently | ✅ Yes | None |

### What Is Actually Missing

1. **Org daily file template** — full markdown structure required (matching specificity of lines 148–178)
2. **"Session work" definition** — what signals that an org was touched? Git commit pattern? Task completion in plan?
3. **B4 display format** — updated template showing where `[personal]`/`[org-name]` tags appear
4. **Directory-missing fallback** — one line: "if `agenda/tasks/` does not exist for an org, skip silently"

---

## Task 2 — `/today — commitments question as multi-select`

**Verdict: NEEDS WORK**  
*Gap description is factually inaccurate. No acceptance criteria. Solution references external pattern without linking it.*

### Gap Verification

**Claim:** "Q3 currently uses a single-select `AskUserQuestion`"  
**Reality:** Q3 (SKILL.md lines 124–129) is a **free-form text prompt**, not an `AskUserQuestion` call. The only `AskUserQuestion` usages in the skill are:
- Step 2 menu (line 43–55): the mode selector
- Q1 energy check (lines 99–110): feeling/energy options

Q2 (lines 118–120) and Q3 (lines 124–129) are both plain conversational prompts. There is no `multiSelect:` or option-list to "convert from" — this is a net-new interaction, not a conversion.

**Impact:** This doesn't block the task from being valid work, but the stated starting point is wrong. The implementer must add an `AskUserQuestion` call from scratch, not modify an existing one.

### Solution Clarity Issues

**Ambiguity 1 — "multiSelect: true, max 3 enforced in instructions"**  
What does "enforced in instructions" mean? If the `AskUserQuestion` tool supports `maxSelections: 3`, specify that. If Claude is supposed to re-ask when >3 selected, say that. Currently: implementer guesses.

**Ambiguity 2 — "Other option covers custom text input (already automatic)"**  
No evidence this is automatic in `AskUserQuestion`. Where is this behavior documented? The task asserts it without citing the tool spec.

**Ambiguity 3 — "same interaction pattern as the /mcp toggle"**  
External reference with no link. Requires reading `/mcp` skill to understand. This is a dependency that should be explicit. If the pattern changes in that skill, this task's spec is silently stale.

**Ambiguity 4 — "week-selected" tasks**  
Task says present "due today, overdue, week-selected" as candidates. "Week-selected" means tasks in `## Selected for This Week` in the weekly file (confirmed: SKILL.md lines 77, 332). The weekly file path is `<agenda-base>weekly/YYYY-WNN.md`. This is inferable but not stated in the task.

**Missing: Empty backlog case**  
No spec for when there are zero pending/in-progress tasks. Fall back to free-form text? Show empty list with only "Other"? Unspecified.

### Acceptance Criteria Assessment

**There are no acceptance criteria in this task file.**

This alone puts it at NEEDS WORK. Without acceptance criteria, there is no definition of done.

### What Is Actually Missing

1. **Acceptance criteria section** — minimum: what does the interaction look like when working correctly? What does it write to the daily file?
2. **Corrected gap description** — Q3 is not a single-select; it's a free-form prompt. Spec should say "add `AskUserQuestion` with `multiSelect: true` to Q3, replacing the current free-form prompt"
3. **Max-3 enforcement mechanism** — `maxSelections: 3` in tool call OR re-ask instruction
4. **Empty backlog behavior** — one sentence
5. **Link to /mcp skill or inline pattern description** — remove external reference dependency

---

## Summary

| Task | Verdict | Primary Blocker |
|---|---|---|
| today-skill-multi-org | NEEDS WORK | Org daily template missing; "session work" undefined; B4 output format unspecified |
| today-commitments-multiselect | NEEDS WORK | No acceptance criteria; gap description factually inaccurate; external reference without link |

Neither task is ready to implement without a spec revision cycle. Both have real and valuable work identified. The multi-org task is closer — gaps are accurate, solution direction is clear, 4 specific additions fix it. The multiselect task needs more foundational spec work.

---
**Re-assessment required:** After spec gaps addressed.
