---
name: awi-submodule-toggle
description: Toggle any AWI repo on or off — orgs, system repos, or a single codebase inside an org. Updates user-submodules.json and clones what you turn on. Replaces awi-org-toggle. Usage: /awi-submodule-toggle <name> [on|off]
---

# /awi-submodule-toggle — Repo Toggle

Toggles what the current operator wants on disk, recorded in their `user-submodules.json`.

## Usage

```
/awi-submodule-toggle <name>                  # flip current state
/awi-submodule-toggle <name> on               # explicitly enable
/awi-submodule-toggle <name> off              # explicitly disable
/awi-submodule-toggle <org>/<codebase> off    # one codebase inside an org
/awi-submodule-toggle status                  # list everything and its state
```

Two kinds of name are accepted: a top-level entry (an org workspace or system repo), or `<org>/<codebase>` for one repo inside an org.

To register a new org or system repo for the first time, add it to `user-submodules.json` directly, then run `/awi-submodule-toggle <name> on`. Codebases need no registration — they come from the org's own `codebases.json`, and toggling one on is enough.

## What "off" does

It records the choice and pushes any uncommitted local work, but **never deletes the directory**. Nothing here is a submodule (see [ADR 0009](../../../docs/adr/0009-manifiestos-json-en-lugar-de-submodulos.md)), so a checkout is ordinary data with no gitlink to restore it from. The script says where it is; deleting it is the operator's call.

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
