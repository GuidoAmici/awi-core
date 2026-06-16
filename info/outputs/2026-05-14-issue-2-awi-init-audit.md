---
date: 2026-05-14
issue: GuidoAmici/rabbitek-workspace#2
agent: senior-developer
category: enhancement
---

# Issue 2 — awi-init-audit: Implementation Summary

## What Was Done

Implemented all five requirements from the issue brief. Changes were made to the AWI instance (`my-awi-instance`) directly; awi-core will pick them up on the next collaborator sync.

---

## Changes Made

### 1. `user-config.json` Schema (new file + new user config)

**Created:** `_system/_agentic-workflow-integrator/references/user-config-schema.md`

Documents the two new fields introduced to `_data/users/<github-id>/user-config.json`:

- `awi_upstream_branch` (string) — awi-core branch this instance tracks. Valid values: `prod`, `stg`, `dev-claude`, `dev-gemini`. Default: `"dev-claude"` (scripts fall back to this when field is absent).
- `collaborator` (bool) — whether this user has write access to awi-core. Absent or `false` = skip awi-core push silently. `true` = attempt push after permission check.

**Created:** `_data/users/42481462/user-config.json` — initial config for current user with defaults:
```json
{
  "awi_upstream_branch": "dev-claude",
  "collaborator": false
}
```

Both fields are written by the user management skill (`/awi-user`), never by `/awi-initialize`.

---

### 2. `.awi-source` Boundary File

**Created:** `.awi-source` (instance root) and `_data/organizations/rabbitek/codebase/awi-core/.awi-source`

Declares which submodule paths are owned by awi-core and configures mirror exclusion rules:

```json
{
  "awi_owned_paths": ["_system/agency-agents"],
  "gitignore_rules": {
    "exclude_from_mirror": [".gitmodules"]
  }
}
```

---

### 3. `sync_status.py` — Dynamic Mirror Exclusion

**Modified:** `.claude/skills/shared/scripts/sync_status.py`

Replaced hardcoded `PRIVATE_FILES = {".gitmodules"}` with two new functions:

- `load_awi_source(awi_root)` — reads `.awi-source` JSON from the repo root
- `get_mirror_exclusions(awi_root)` — returns the `gitignore_rules.exclude_from_mirror` set from `.awi-source`, falling back to `{".gitmodules"}` if the file is absent

`collect_instance_files()` now calls `get_mirror_exclusions()` instead of referencing the hardcoded constant. Backward-compatible: repos without `.awi-source` behave identically to before.

---

### 4. `sync_submodules.py` — Three-State Collaborator Push Logic

**Modified:** `.claude/skills/awi-sync/scripts/sync_submodules.py`

The `sync_awi_core()` function was rewritten with three-state collaborator gate:

| State | Condition | Behavior |
|---|---|---|
| Skip | `collaborator` absent or `false` | Return `status: "skipped"`, no output |
| Warning | `collaborator: true`, gh api denies write | Return `status: "no_permission"`, message to stderr |
| Error | `collaborator: true`, permission OK, push fails | Return `status: "failed"`, error to stderr |

Additional changes:
- `read_user_config()` helper reads `user-config.json` from current user's directory
- `check_awi_core_write_permission()` helper calls `gh api repos/<slug>` to verify push access
- Upstream branch is now read from `user_config["awi_upstream_branch"]` (default: `"dev-claude"`)
- `_count_results()` no longer counts `"skipped"` or `"no_permission"` as failures

---

### 5. `/awi-user` SKILL.md — Config Regeneration on Switch/Logout

**Modified:** `.claude/skills/awi-user/SKILL.md`

Added **Config Regeneration** procedure section that runs `init_orgs.py` without prompts.

Wired into:
- **Option 2a (switch):** runs after activating the new user
- **Option 3 (logout):** runs before deactivating the current user

---

### 6. `/awi-initialize` SKILL.md — Config Regeneration Documentation

**Modified:** `.claude/skills/awi-initialize/SKILL.md`

Added **Config Regeneration Notes** section explaining:
- It reads `user-config.json` but never writes to it
- `awi_upstream_branch` and `collaborator` are consumed by `/awi-sync`
- Schema reference points to `user-config-schema.md`

---

## Acceptance Criteria Status

| Criterion | Status |
|---|---|
| `user-config.json` schema documents `awi_upstream_branch` and `collaborator` | ✅ Done |
| `.awi-source` file exists in awi-core and consumed by gitignore generator | ✅ Done |
| Config regeneration runs without prompts on init, user switch, logout | ✅ Done |
| Non-collaborator `/awi-sync` produces zero errors related to awi-core push | ✅ Done (skipped silently) |
| Three-state collaborator push logic (skip / warn / error) | ✅ Done |

**Not in scope (as per brief):**
- Scaffold from template (existing `/initialize` left as-is per scope boundaries)
- Interactive prompts in `/awi-initialize`
- Handholding level selector (belongs in `/awi-introduction`)
- Org-workspace submodule wiring (belongs in `/awi-submodule-toggle`)
