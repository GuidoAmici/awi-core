---
name: awi-core-sync-status
description: Report sync status between AWI (private) and awi-core (public forkable repo). Shows which whitelisted files are ok, drifted, missing from core, or extra. Usage: /awi-core-sync-status
---

# /awi-core-sync-status — Sync Status

Compares AWI against awi-core for all files covered by `.claude/config/public-whitelist`.

## Usage

```
/awi-core-sync-status
```

---

## Steps

### Step 1 — Run the status script

```bash
python3 .claude/skills/awi-core-sync-status/scripts/sync_status.py
```

### Step 2 — Interpret and present output

The script outputs a table with four status values:

| Status | Meaning |
|--------|---------|
| `ok` | File is identical in AWI and awi-core |
| `DRIFT` | File exists in both but content differs — awi-core is behind |
| `MISSING from core` | File is whitelisted in AWI but absent from awi-core |
| `EXTRA in core` | File exists in awi-core but is not covered by the whitelist |

Files with `kind: context` in frontmatter are excluded (opt-out override).

### Step 3 — If drift or missing files found, offer to sync

Ask the user:
```
Found <N> file(s) out of sync. Run /awi-core-push to mirror them now?
```

Do not push automatically. Wait for confirmation.
