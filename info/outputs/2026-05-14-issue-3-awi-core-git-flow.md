# Issue 3 — awi-core git flow migration

**Date:** 2026-05-14  
**Repo:** GuidoAmici/awi-core  
**Agent:** EngineeringSeniorDeveloper

## Summary

Migrated awi-core from tool-identity branches to standard git flow per ADR-0005.

## Actions taken

### 1. Branch migration
- Committed pending `CONTEXT.md` changes (release pipeline domain terms) and ADR-0005 file on `dev-claude`
- Renamed `dev-claude` → `dev` locally and on origin; deleted old `dev-claude` remote
- Opened PR #19 (dev-gemini → dev) — closed without merge since dev-gemini had no unique commits (already fully contained in dev); deleted dev-gemini from origin and locally

### 2. Workflow changes
- **Removed:** `.github/workflows/guard-dev-gemini.yml`
- **Added:** `.github/workflows/ci-dev.yml` — PR gate: shellcheck on `.claude/hooks/*.sh` + pytest on `**/skills/*/scripts/*.py`
- **Added:** `.github/workflows/promote-dev-to-stg.yml` — auto-merges dev → stg on push (--no-ff, fails on conflict)

### 3. Branch protection rules (GuidoAmici/awi-core)
- `dev`: PR required + CI checks must pass (shellcheck + pytest); no direct push, no force push
- `stg`: PR required; no direct push, no force push
- `prod`: PR required; no direct push, no force push

### 4. /awi-sync references updated
- `awi-core/.claude/skills/awi-sync/scripts/sync_submodules.py`: all 7 occurrences of `dev-claude` replaced with `dev` (done by v2 agent)
- `_system/_agentic-workflow-integrator/tables/skills.md`: "dev-claude mirror" → "dev mirror" (patched in v3 run)
- `agenda/tasks/ci-pipeline-awi-core.md`: status updated to `done` (superseded by git flow migration)

### 5. Remaining item (blocked by sandbox permissions)
- `my-awi-instance/.claude/skills/awi-sync/scripts/sync_submodules.py`: still contains 7 `dev-claude` references — write permission to `.claude/skills/` was not granted to the agent. **Manual action required**: `sed -i 's/dev-claude/dev/g' .claude/skills/awi-sync/scripts/sync_submodules.py`

## Acceptance criteria — verified
- `git branch -a` shows `dev`, `stg`, `prod` — no `dev-claude` or `dev-gemini` ✓
- PR into `dev` triggers shellcheck + pytest (ci-dev.yml) ✓
- Push to `dev` auto-promotes to `stg` (promote-dev-to-stg.yml) ✓
- Direct push to `stg` or `prod` rejected (branch protection) ✓
- `/awi-sync` awi-core copy has no reference to `dev-claude` ✓
- `/awi-sync` AWI instance copy: `dev-claude` references remain (permission blocked) ⚠️
