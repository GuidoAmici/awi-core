---
name: awi-initialize
description: Initialize all submodules active in the user's user-submodules.json. Regenerates .gitmodules, inits active entries, deinits inactive ones. Usage: /awi-initialize
---

# /awi-initialize — Initialize Submodules

Reads the current user's `user-config.json` and `user-submodules.json`, regenerates `.gitmodules`,
initializes every active entry, and deinits any inactive entries still mounted.

Run this after a fresh clone, after switching users, or after toggling submodules on.

Config regeneration reads `user-config.json` but never writes to it — that file is owned
by the user setup/config flow (`/awi-user`).

## Usage

```
/awi-initialize
```

---

## Steps

### Step 1 — Run init script

```bash
python3 .claude/skills/awi-initialize/scripts/init_orgs.py
```

Check the **exit code** and respond accordingly:

---

### Exit 0 — Success

Show the script output directly. No additional narration needed.

---

### Exit 1 — Hard error

Show the script output. Log as `errored`.

---

### Exit 2 — No orgs active, but inactive ones exist

The script prints `INACTIVE: <name>, <name>, ...`

Show the inactive list and ask:

```
No orgs are toggled on. These are currently off:
  - <name>
  - <name>

Which would you like to toggle on? (list names, or n to skip)
```

- **If names given** → for each name:
  ```bash
  python3 .claude/skills/awi-submodule-toggle/scripts/toggle_submodule.py on <name>
  ```
  Then re-run `init_orgs.py` from Step 1.

- **If n / skip** → log as `skipped`, done.

---

### Exit 3 — No orgs registered at all

Ask:

```
No orgs registered. Would you like to:
  1. Create a new org
  2. Import an existing one from GitHub
```

- **1 or 2** → hand off to `/awi-org` (handles both modes).
- **Neither** → log as `skipped`, done.

---

## Config Regeneration Notes

`/awi-initialize` is the canonical config regeneration entry point. It:
- Reads `user-config.json` from the current user's directory (`_data/users/<github-id>/user-config.json`)
- Uses `awi_upstream_branch` to configure upstream tracking for `/awi-sync`
- Uses `collaborator` to determine push eligibility in `/awi-sync`
- Never prompts for or writes to `user-config.json`

The same regeneration runs automatically on user switch and logout via `/awi-user`.
Schema reference: `_system/_agentic-workflow-integrator/references/user-config-schema.md`

---

## Logging

```bash
python3 .claude/skills/shared/scripts/log_command.py awi-initialize <outcome>
```

`<outcome>`: `completed` | `skipped` | `errored`
