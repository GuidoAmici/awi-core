---
name: awi-sync
description: Sync all AWI submodules (direct + nested). Commits local changes, pulls, and pushes each repo. Updates _data/submodules.md. Usage: /awi-sync
---

# /awi-sync — Submodule Sync

Scans all submodules registered in AWI and nested client repos, syncs each to `main`, and updates the registry in `_data/submodules.md`.

## Usage

```
/awi-sync
```

---

## Steps

### Step 1 — Run the sync script

```bash
python3 .claude/skills/awi-sync/scripts/sync_submodules.py
```

The script handles everything:
- Discovers all submodules (AWI-level + nested inside each client)
- For each: checks clone status → removes `.gitkeep` from populated folders → commits any local changes (`git add -A`) → checks out tracked branch → pulls → pushes
- Updates `_data/submodules.md` (Mermaid class styles + registry table)

### Step 2 — Present the report to the user

Show the script output verbatim. Then add a one-line summary:

- If all synced: `All submodules are up to date.`
- If failed: `N repo(s) could not be synced. See errors above.`

### Step 3 — Show the updated graph

After the report, display the updated Mermaid graph from `_data/submodules.md` so the user can see the new state visually.

---

## Exit codes from the script

| Code | Meaning |
|---|---|
| `0` | All submodules synced successfully |
| `1` | One or more submodules failed |

---

## Logging

At the end of this skill — regardless of outcome — log the invocation:

```bash
python3 .claude/skills/shared/scripts/log_command.py awi-sync <outcome>
```

`<outcome>`: `completed` | `skipped` | `errored`
