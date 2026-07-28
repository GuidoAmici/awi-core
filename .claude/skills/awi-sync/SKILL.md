---
name: awi-sync
description: Sync every AWI repo — workspaces and the codebases inside them. Commits local changes, pulls, and pushes each one. Updates _data/submodules.md. Usage: /awi-sync
---

# /awi-sync — Repo Sync

Syncs every repo this operator has on disk to its tracked branch and updates the registry in `_data/submodules.md`.

Discovery comes from the manifests, not from `.gitmodules`: `user-submodules.json` for orgs and system repos, each org's `codebases.json` for its code. Nothing here is a submodule — see [ADR 0009](../../../docs/adr/0009-manifiestos-json-en-lugar-de-submodulos.md).

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
- Discovers every repo from the manifests (workspaces + the codebases inside each org)
- For each: checks clone status → commits any local changes (`git add -A`) → checks out tracked branch → pulls → pushes
- Updates `_data/submodules.md` (Mermaid class styles + registry table)
- Always prints the full report (summary + Mermaid graph; breakdown on failure)

Repos marked `upstream` are read-only mirrors of third-party code: fetched and hard-reset to match upstream, never committed to or pushed.

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
| `0` | All repos synced successfully |
| `1` | One or more repos failed |
