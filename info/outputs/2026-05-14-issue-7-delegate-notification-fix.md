# Issue 7 — Delegate Notification Fix

**Date:** 2026-05-14  
**Status:** Completed

## Root Causes Found

### 1. Hook path resolution — missing fallback (`check-delegates.sh`)

The hook derived the inbox path exclusively from `$CLAUDE_PROJECT_DIR`:

```bash
INBOX="$CLAUDE_PROJECT_DIR/.claude/tmp/delegates/inbox.md"
```

If `CLAUDE_PROJECT_DIR` is unset (e.g., in sub-shell contexts, older Claude Code
versions, or edge cases during hook firing), the path collapsed to
`/.claude/tmp/delegates/inbox.md`, which doesn't exist. The script exited
silently with code 0 — no notification, no error.

**Fix:** Derive `PROJECT_ROOT` from the script's own location first; use
`$CLAUDE_PROJECT_DIR` only as fallback.

### 2. Race condition on inbox clear (`check-delegates.sh`)

The original pattern was:
```bash
content=$(cat "$INBOX")   # read
...
> "$INBOX"                # truncate
```

Between the `cat` and the `>`, a delegate completing at that instant would write
its entry to the inbox — and then `>` would wipe it. Silent loss, no retry.

**Fix:** Atomic `mv "$INBOX" "$INBOX_TMP"` before reading. New delegate
completions then create a fresh `inbox.md` while we process the temp file.
Zero entries lost.

### 3. Silent inbox write failures (`delegate_run.py`)

The inbox write in `run_worker()` had no error handling:
```python
with open(inbox_file, "a", encoding="utf-8") as f:
    f.write(entry)
```

Any `OSError` (disk full, permission denied, path error) was silently swallowed.
Additionally, no `fsync()` call meant the OS could buffer the write; the hook
could fire before the data reached disk.

**Fix:**
- Wrapped in `try/except` — failures print a WARNING to stderr (appears in
  `output.log`)
- Added `f.flush()` + `os.fsync(f.fileno())` to guarantee durability before
  the agent process exits

## `delegate_monitor.py` — Stuck Detection Audit

`is_stuck()` with `STUCK_THRESHOLD_S = 90` is **correct**. All test cases pass:

| Scenario | Expected | Result |
|---|---|---|
| Running, log active 30s ago | Not stuck | ✓ |
| Running, log idle 120s | Stuck | ✓ |
| Running, no log yet, started 30s | Not stuck | ✓ |
| Running, no log yet, started 120s | Stuck | ✓ |
| Completed, old log | Not stuck | ✓ |

The 90s threshold is appropriate: with `stdbuf -oL`, each Claude output line
immediately updates `output.log` mtime. 90 seconds of silence is a reliable
signal of a genuinely stuck agent (not a false positive from internal thinking
pauses — Claude writes tokens continuously during processing).

## Files Changed

| File | Change |
|---|---|
| `.claude/hooks/check-delegates.sh` | Script-relative path resolution; atomic `mv`-based read-clear; robust whitespace check |
| `.claude/skills/delegate-issue/scripts/delegate_run.py` | `try/except` + `flush()` + `fsync()` on inbox write |

## End-to-End Verification

1. Hook surfaces 2 previously-stuck notifications (issue-9, issue-35) ✓
2. Inbox is atomically cleared (no file left after hook runs) ✓
3. Hook exits cleanly (code 0) on empty inbox ✓
4. Concurrent writes test: 3 delegates complete simultaneously — all 3 entries
   captured, inbox cleaned up ✓
