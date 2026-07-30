---
name: awi-initialize
description: Clone every repo active in the user's user-submodules.json, plus each org's active codebases. Usage: /awi-initialize
---

# /awi-initialize — Materialise Repos

Reads the current user's `user-submodules.json` and each org's `codebases.json`, then clones
whatever is missing. Nothing here is a submodule — see
[ADR 0009](../../../docs/adr/0009-manifiestos-json-en-lugar-de-submodulos.md).

Run this after a fresh clone, after switching users, or after toggling something on.

Cloning happens in two passes: org workspaces and system repos first, then codebases — an org's
`codebases.json` only becomes readable once the workspace itself is on disk.

An existing checkout is never touched. Init will not move the operator off the branch they are
working on; the shared-context cycle owns that (see `context_sync.py`).

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

### Exit 4 — Actives are fine, but inactive entries are still on disk

The script prints one `MOUNTED_INACTIVE: <name>\t<path>` line per entry.

Everything active was materialised — this is not a failure. These are directories the operator
has toggled off but that still hold data. **Never delete them automatically**: without a gitlink
there is nothing to restore them from.

Ask about each one separately:

```
'<name>' is off but still on disk at <path>.
Delete it, or leave it? (delete / leave)
```

- **delete** → confirm the repo has nothing unpushed, then `rm -rf <path>`.
- **leave** → say nothing more about it.

Log as `completed` either way.

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

## Where the declarations live

| Manifest | Location | Scope | Declares |
|---|---|---|---|
| `user-submodules.json` | `_data/users/<github-id>/` | one operator, private | which orgs and system repos they want, with url/path/branch, and which codebases of each org |
| `codebases.json` | `_data/organizations/<org>/` | versioned, whole team | which repos make up the org and on what branch |

A codebase active in `user-submodules.json` but absent from the org's `codebases.json` is reported
as a warning, not skipped silently — it usually means a rename or a repo dropped from the org.

The same materialisation runs automatically on user switch via the `gh auth` hook.

---

## Logging

```bash
python3 .claude/skills/shared/scripts/log_command.py awi-initialize <outcome>
```

`<outcome>`: `completed` | `skipped` | `errored`
