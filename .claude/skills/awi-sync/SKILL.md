---
name: awi-sync
description: Sync all AWI submodules (direct + nested). Commits local changes, pulls, and pushes each repo. Updates _data/submodules.md. Usage: /awi-sync
---

# /awi-sync — Submodule Sync

Scans all submodules registered in AWI and nested client repos, syncs each to their tracked branch, and updates the registry in `_data/submodules.md`.

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
- Prints a 1-line summary and logs the invocation

### Step 2 — Show output verbatim

The script always outputs a 1-line summary: `✓ N synced   ✗ M failed`

Mention available flags:
- `--full-report` — also prints the Mermaid submodule graph
- `--breakdown` — also prints a per-submodule text breakdown

---

## Exit codes from the script

| Code | Meaning |
|---|---|
| `0` | All submodules synced successfully |
| `1` | One or more submodules failed |
