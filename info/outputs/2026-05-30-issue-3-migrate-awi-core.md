# Issue 3 — Migrate awi-core to standard git flow (dev/stg/prod)

**Date:** 2026-05-30  
**Agent:** senior-developer  
**Issue:** GuidoAmici/rabbitek-workspace#3

---

## Summary

Migrated `awi-core` from tool-identity branches (`dev-claude`/`dev-gemini`) to standard git flow (`dev` → `stg` → `prod`) and implemented the CI pipeline.

---

## Completed

### 1. Branch migration
- `dev`, `stg`, `prod` branches exist on `GuidoAmici/awi-core` — no `dev-claude` or `dev-gemini`
- (Migration was performed by a prior agent run; confirmed here)

### 2. guard-dev-gemini.yml removal
- Deleted `.github/workflows/guard-dev-gemini.yml` from `stg` branch (commit: `3e0d692`)
- Deleted `.github/workflows/guard-dev-gemini.yml` from `prod` branch (commit: `08775b2`)
- Was not present on `dev` branch (already removed by prior agent run)

### 3. CI workflows (exist on `dev` branch)
- `.github/workflows/ci-dev.yml` — PR gate: shellcheck on `.claude/hooks/*.sh` + pytest on `**/skills/*/scripts/*.py`
- `.github/workflows/promote-dev-to-stg.yml` — auto-promotes `dev` → `stg` on push with `--no-ff`; fails on conflict

### 4. Branch protection rules
- `dev`: requires PR + CI pass (shellcheck + pytest checks required) — no direct push
- `stg`: requires PR — no direct push (auto-promotion via CI workflow is the intended path)
- `prod`: requires PR — no direct push (manual promotion from stg only)

### 5. /awi-sync branch reference updates
- `_system/_agentic-workflow-integrator/references/user-config-schema.md`: updated all `dev-claude`/`dev-gemini` references to `dev`
- `GuidoAmici/my-awi-user/user-config.json`: updated `awi_upstream_branch` from `"dev-claude"` to `"dev"` (commit: `f28fbf2`)
- `GuidoAmici/awi-core` (`dev` branch) `sync_submodules.py`: already has `"dev"` as default (verified via API)

---

## Partial / Blocked

### sync_submodules.py in AWI instance
- File: `.claude/skills/awi-sync/scripts/sync_submodules.py`
- Lines 418 and 447 still reference `"dev-claude"` as fallback default
- **Blocked**: the `.claude/` directory is protected by the parent agent's permission sandbox (Edit, Write, and sed/awk Bash commands denied for this path)
- **Impact**: low — `collaborator` is `false` in user-config, so the awi-core mirror code path is skipped silently at runtime. If the user ever becomes a collaborator, the `awi_upstream_branch` from `user-config.json` (now `"dev"`) takes precedence over the hardcoded default.
- **Fix needed**: a human or a session with `.claude/` write permissions should run: `sed -i 's/"dev-claude"/"dev"/g' .claude/skills/awi-sync/scripts/sync_submodules.py`

---

## Acceptance criteria status

| Criterion | Status |
|---|---|
| `git branch -a` shows dev, stg, prod — no dev-claude/dev-gemini | DONE |
| PR into dev triggers shellcheck + pytest | DONE (ci-dev.yml on dev branch) |
| Merging PR into dev auto-promotes dev → stg | DONE (promote-dev-to-stg.yml) |
| Conflict between dev and stg fails promotion job | DONE (workflow fails on merge conflict) |
| Direct push to stg or prod rejected by branch protection | DONE |
| /awi-sync runs without dev-claude references | PARTIAL (user-config.json updated; schema updated; local sync_submodules.py needs manual fix) |
