---
name: awi-submodule-toggle
description: Toggle any AWI submodule on or off (orgs and system repos). Updates user-submodules.json, regenerates .gitmodules, and inits/deinits the working tree. Replaces awi-org-toggle. Usage: /awi-submodule-toggle <name> [on|off]
---

# /awi-submodule-toggle — Submodule Toggle

Toggles any entry in the current user's `user-submodules.json` — org workspaces and system repos alike.

## Usage

```
/awi-submodule-toggle <name>           # flip current state
/awi-submodule-toggle <name> on        # explicitly enable
/awi-submodule-toggle <name> off       # explicitly disable
/awi-submodule-toggle status           # list all entries and state
```

To register a new submodule for the first time, add it to `user-submodules.json` directly, then run `/awi-submodule-toggle <name> on`.

---

## Steps

### Step 1 — Run the toggle script

```bash
python3 .claude/skills/awi-submodule-toggle/scripts/toggle_submodule.py <args>
```

Show the script output directly.

### Step 2 — Log

```bash
python3 .claude/skills/shared/scripts/log_command.py awi-submodule-toggle completed
```
