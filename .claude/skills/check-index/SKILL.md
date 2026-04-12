---
name: check-index
description: Audit every folder in _system/ and _clients/ for missing .abstract.md and .overview.md files. Reports gaps without modifying anything.
allowed-tools: Bash
model: haiku
---

# /check-index — Context File Audit

Scans every folder in `_system/` and all initialized `_clients/<name>/` subtrees and reports which ones are missing `.abstract.md` or `.overview.md`.

This is a read-only audit. It never creates or modifies files. To fix gaps, run `/reindex`.

## Steps

### 1. Discover all folders

```bash
find _system -mindepth 1 -type d | sort
find _clients -mindepth 1 -maxdepth 3 -type d | sort
```

### 2. Skip rules

Do NOT flag as missing for:
- Git submodule roots inside `_clients/<name>/codebase/` or `_clients/<name>/documentation/` — they have their own indexes
- `node_modules/`, `.git/`, `.claude/`
- Folders with only a single file and no subfolders (check at runtime)
- Uninitialized submodule paths (empty directories)

### 3. For each folder, check

- Does `.abstract.md` exist?
- Does `.overview.md` exist?

`.overview.md` is only expected for folders with 3+ subfolders or significant structure — mark absence as a **warning**, not an error.

`.abstract.md` is expected in every meaningful folder — mark absence as an **error**.

### 4. Output format

```
FOLDER                                          .abstract.md   .overview.md
_system/                                        OK             OK
_system/users/                                  MISSING        WARNING
_clients/                                     OK             —
_clients/guido-amici/agenda/                  OK             OK
...
```

Then print counts:
- Errors (missing `.abstract.md`): N
- Warnings (missing `.overview.md` in complex folders): N
- OK: N

If everything is present, say so clearly.
