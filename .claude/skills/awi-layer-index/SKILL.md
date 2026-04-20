---
name: awi-layer-index
description: Audit and fix OpenViking L0/L1 context files (.abstract.md, .overview.md) across _system/, _data/users/, and _data/organizations/. Step 1 always audits; step 2 optionally fixes gaps.
allowed-tools: Read, Write, Bash, Glob
model: sonnet
---

# /awi-layer-index — Context File Audit & Fix

Two-step skill: **audit** gaps, then optionally **fix** them by creating or updating `.abstract.md` (L0) and `.overview.md` (L1) files per the OpenViking context navigation convention.

Invocation modes:
- `/awi-layer-index` — run audit, then ask whether to fix
- `/awi-layer-index audit` — audit only, never write
- `/awi-layer-index fix` — audit then immediately fix without asking

---

## Context Files Defined

| File | Level | Format | When required |
|------|-------|--------|---------------|
| `.abstract.md` | L0 | Plain text, one sentence, no frontmatter | Every meaningful folder — **ERROR** if missing |
| `.overview.md` | L1 | Markdown with heading, folder map, conventions | Folders with 3+ subfolders or non-obvious structure — **WARNING** if missing |

---

## Step 1 — Discover All Folders

```bash
find _system -mindepth 1 -type d | sort
find _data/users -mindepth 1 -maxdepth 3 -type d | sort
find _data/organizations -mindepth 1 -maxdepth 3 -type d | sort
```

**Skip rules — do NOT flag or write for:**
- Git submodule roots inside `_data/organizations/<name>/codebase/` or `_data/organizations/<name>/documentation/` — they have their own indexes
- `node_modules/`, `.git/`, `.claude/`
- Folders with only a single file and no subfolders (check at runtime)
- Uninitialized submodule paths (empty directories)

---

## Step 2 — Audit

For each folder, check presence of `.abstract.md` and `.overview.md`:

```
FOLDER                                          .abstract.md   .overview.md
_system/                                        OK             OK
_data/users/                                    OK             —
_data/users/<github-id>/                        OK             OK
_data/organizations/                                  OK             —
_data/organizations/<name>/agenda/                    OK             OK
...
```

Then print counts:
- **Errors** (missing `.abstract.md`): N
- **Warnings** (missing `.overview.md` in complex folders): N
- **OK**: N

If everything is present, say so clearly.

---

## Step 3 — Fix (if requested)

For each gap found in the audit, create or update the missing file.

### Writing `.abstract.md` (L0)

- One sentence only. No frontmatter. No heading.
- Describe *what the folder contains*, not how to use it.
- Start with the noun — not "This folder contains…"
- Match voice of existing abstracts:
  - `Atomic work items with status, owner, and product/app/feature context — the lowest level of the task hierarchy.`
  - `Unscoped concepts and feature ideas not yet promoted to projects or tasks — the inbox for future work.`

### Writing `.overview.md` (L1)

Only for folders with 3+ subfolders or non-obvious rules:

```markdown
# <folder-path> — Overview

<1–2 sentence summary of purpose and scope>

## Folder map

| Folder / File | Purpose |
|---|---|
| `subfolder/` | What it contains |
| `key-file.md` | What it is |

## Conventions

<Naming rules, frontmatter requirements, or workflow rules specific to this folder.>
```

- Use vault path as heading (e.g., `# _system/chief-of-staff — Overview`)
- Omit **Conventions** section if no real rules exist
- Keep under ~30 lines

### Codebase app pointer stubs

Each app submodule in `_data/organizations/<name>/codebase/` gets `.abstract.md` as a pointer stub:

```
Context: _data/organizations/<name>/documentation/<app>.md
```

Discover app submodule folders at runtime:
```bash
git submodule status | awk '{print $2}' | grep "^_data/organizations/"
```

### Workspace submodule roots

Each `_data/organizations/<name>/` is a git submodule root. Do NOT descend into uninitialized submodules. If initialized (content present), index it. If bare pointer, skip.

### After writing

```bash
git status --short | grep -E "\.abstract\.md|\.overview\.md"
```

Report summary:

| Tree | Created | Updated | Skipped |
|------|---------|---------|---------|
| `_system/` | N | N | N |
| `_data/users/` | N | N | N |
| `_data/organizations/` | N | N | N |

---

## Logging

```bash
python3 .claude/skills/shared/scripts/log_command.py awi-layer-index <outcome>
```

`<outcome>`: `completed` | `skipped` | `errored`
