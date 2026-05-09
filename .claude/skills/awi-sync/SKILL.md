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
python3 .claude/skills/awi-sync/scripts/sync_submodules.py --full-report
```

The script handles everything:
- Discovers all submodules (AWI-level + nested inside each client)
- For each: checks clone status → removes `.gitkeep` from populated folders → commits any local changes (`git add -A`) → checks out tracked branch → pulls → pushes
- Updates `_data/submodules.md` (Mermaid class styles + registry table)
- Prints output at the requested verbosity level

Capture the full output in memory. Show only the 1-line summary to the user.

### Step 2 — Offer a breakdown

Use the AskUserQuestion tool to ask:

- **question:** "Want more detail?"
- **options:** `["No", "Breakdown", "Full report"]`

If the user picks **Breakdown** or **Full report**, display the already-captured output — do NOT re-run the script.
If the user picks **No**, stop.

---

## Exit codes from the script

| Code | Meaning |
|---|---|
| `0` | All submodules synced successfully |
| `1` | One or more submodules failed |
