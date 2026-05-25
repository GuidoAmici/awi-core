# Issue #17 — awi-core as Source of Truth

**Date:** 2026-05-25
**Agent:** minimal-change-engineer

## Summary

Synced awi-core to match the instance, making it the authoritative source of truth. Three change categories executed.

## Changes applied

### Skills added (11)

Copied from `instance/.agents/skills/` to `awi-core/.claude/skills/` as real directories (not symlinks):

- `diagnose/` — SKILL.md + scripts/hitl-loop.template.sh
- `grill-me/` — SKILL.md
- `grill-with-docs/` — SKILL.md + ADR-FORMAT.md + CONTEXT-FORMAT.md
- `improve-codebase-architecture/` — SKILL.md + DEEPENING.md + INTERFACE-DESIGN.md + LANGUAGE.md
- `prototype/` — SKILL.md + LOGIC.md + UI.md
- `tdd/` — SKILL.md + 5 reference docs
- `to-issues/` — SKILL.md
- `to-prd/` — SKILL.md
- `triage/` — SKILL.md + AGENT-BRIEF.md + OUT-OF-SCOPE.md
- `write-a-skill/` — SKILL.md
- `zoom-out/` — SKILL.md

### Hooks removed (3)

- `.claude/hooks/notify-sound.wav`
- `.claude/hooks/stop-sound.sh`
- `.claude/hooks/stop-sound.wav`

### settings.json patched (1 line)

- `PostToolUse` matcher: `Write|Edit|Bash` → `Write|Edit`
- `UserPromptSubmit` check-delegates PS1 fallback: preserved as-is

## Out of scope (noted, not done)

- `.agents/skills/` structure — the `caveman` symlink inside `to-issues/` was not included; resolving `.agents/` vs `.claude/` distinction is issue #18 or separate.
- `employees.json` — issue #16
- Deleting `GuidoAmici/my-awi-instance` — manual step after merge

## Commits

- `9e3ed4e` — initial sync (hooks + settings + symlinks)
- `115dfa7` — fix: replace symlinks with real directories
