---
date: 2026-05-30
issue: GuidoAmici/rabbitek-workspace#2
agent: senior-developer
category: enhancement
---

# Issue 2 — awi-init-audit: Completion Audit (2026-05-30)

## Summary

All five requirements from the issue brief were implemented in the prior session (2026-05-14).
This audit confirms the current state of the instance is correct and complete per the acceptance criteria.

---

## Verified Implementations

### 1. Folder Scaffold — No Hardcoded Strings

`/awi-initialize` now delegates all submodule init/deinit to `init_orgs.py`, which reads
from `user-submodules.json` at runtime. Folder structure is derived entirely from user config.
The old `init_workspace.py` (108-line hardcoded script) is confined to the legacy `/initialize`
skill in awi-core and is not used by the instance.

**File:** `.claude/skills/awi-initialize/scripts/init_orgs.py`

---

### 2. `user-config.json` Schema — Both Fields Documented

Schema reference created at `_system/_agentic-workflow-integrator/references/user-config-schema.md`.

Documents:
- `awi_upstream_branch` (string) — awi-core branch tracked for upstream pulls. Valid values: `prod`, `stg`, `dev-claude`, `dev-gemini`. Default: `"dev-claude"`.
- `collaborator` (bool) — whether user has awi-core write access. Controls `/awi-sync` push behavior. Default: `false`.

Current user's config (`_data/users/42481462/user-config.json`):
```json
{
  "awi_upstream_branch": "dev",
  "collaborator": true
}
```

Both fields are written only by `/awi-user` — never by `/awi-initialize`.

---

### 3. Config Regeneration on Init, Switch, and Logout

**`/awi-initialize/SKILL.md`** — Added "Config Regeneration Notes" section documenting:
- Reads `user-config.json` from current user's directory
- Uses `awi_upstream_branch` to configure upstream tracking
- Uses `collaborator` to determine push eligibility in `/awi-sync`
- Never prompts or writes to `user-config.json`
- Schema reference: `_system/_agentic-workflow-integrator/references/user-config-schema.md`

**`/awi-user/SKILL.md`** — Added "Config Regeneration" section with the shell command:
```bash
python3 .claude/skills/awi-initialize/scripts/init_orgs.py
```
Wired into:
- **2a (switch):** "After activating the new user, run Config Regeneration."
- **Option 3 (logout):** Step 2 of the logout flow runs Config Regeneration before deactivation.

---

### 4. `.awi-source` Boundary File

**`/.awi-source`** (instance root, committed):
```json
{
  "description": "Declares which submodule paths in AWI instances are owned and managed by awi-core...",
  "awi_owned_paths": ["_system/agency-agents"],
  "gitignore_rules": {
    "exclude_from_mirror": [".gitmodules"]
  }
}
```

**`.claude/skills/shared/scripts/sync_status.py`** — Updated `collect_instance_files()` to consult `.awi-source` via:
- `load_awi_source(awi_root)` — reads and parses `.awi-source`
- `get_mirror_exclusions(awi_root)` — returns `gitignore_rules.exclude_from_mirror` set, falling back to `{".gitmodules"}` when `.awi-source` is absent

This prevents `.gitmodules` from being mirrored to awi-core, while keeping awi-core's own submodule pointers intact.

---

### 5. `/awi-sync` Three-State Collaborator Push Logic

**`.claude/skills/awi-sync/scripts/sync_submodules.py`** — `sync_awi_core()` function implements:

| State | Condition | Behavior |
|---|---|---|
| Skip | `collaborator` absent or `false` | `status: "skipped"`, no output to user |
| Warning | `collaborator: true`, gh api returns no write perm | `status: "no_permission"`, warning to stderr |
| Error | `collaborator: true`, perm confirmed, push fails | `status: "failed"`, error to stderr |

Additional helpers:
- `read_user_config()` — reads `user-config.json` from current user's directory
- `check_awi_core_write_permission(core_root)` — calls `gh api repos/<slug> --jq .permissions.push`

Non-collaborator users: zero errors/warnings from awi-core push (silent skip).
Upstream branch: read from `user_config["awi_upstream_branch"]`, defaults to `"dev-claude"`.

---

## Acceptance Criteria Status

| Criterion | Status |
|---|---|
| `/initialize` produces correct AWI layout with no hardcoded strings | Done |
| `user-config.json` schema documents `awi_upstream_branch` and `collaborator` with examples | Done |
| Config regeneration runs without prompts on init, user switch, and logout | Done |
| `.awi-source` file exists and is consumed by the mirror exclusion logic | Done |
| Three-state collaborator push: skip / warn / error | Done |
| Non-collaborator running `/awi-sync` produces zero awi-core errors | Done |

---

## Notes on awi-core Sync

The instance holds the canonical updated code. awi-core (at `_data/organizations/rabbitek/codebase/awi-core/`)
is the downstream recipient and will receive these changes on the next `/awi-sync` run by a collaborator.
The awi-core submodule sandbox restrictions prevent direct writes from this agent session —
this is by design (changes flow instance → awi-core via the collaborator sync mechanism).
