---
name: reindex
description: Re-index the _system/ tree and all _clients/ folders by creating or updating .abstract.md (L0) and .overview.md (L1) files, following the OpenViking context navigation convention.
---

# /reindex — Context Navigation Re-index

Walks `_system/` and all `_clients/<name>/` subtrees, ensuring all folders have accurate `.abstract.md` and `.overview.md` files per the OpenViking L0/L1 convention.

## When to run

- After renaming, moving, or restructuring folders inside `_system/` or `_clients/`
- After adding new workspace submodules or app submodules
- When context files feel stale or out of sync with actual contents

## Context files defined

| File | Level | Format | When to create |
|------|-------|--------|----------------|
| `.abstract.md` | L0 | Plain text, one sentence, no frontmatter | Every meaningful folder |
| `.overview.md` | L1 | Markdown with heading, folder map table, taxonomy/rules | Top-level and mid-level folders with structure worth explaining |

**Skip** `.abstract.md` / `.overview.md` for:
- Folders that are git submodule roots (they have their own `CLAUDE.md` / `_index.md`)
- `node_modules/`, `.git/`, `.claude/`
- Folders with only a single file and no subfolders

## Steps

### 1. Discover all folders

```bash
find _system _clients -mindepth 1 -type d | sort
```

Also check the root `_system/` and `_clients/` folders themselves.

### 2. For each folder — decide what's needed

For every folder path:

1. List its direct contents: files and immediate subdirectories
2. Read existing `.abstract.md` and `.overview.md` if present
3. Decide: **create**, **update**, or **skip**
   - **Create** — file is missing
   - **Update** — file exists but references old paths, wrong folder names, or missing subdirs added since it was written
   - **Skip** — file exists and accurately reflects current contents

### 3. Write `.abstract.md` (L0)

- One sentence only. No frontmatter. No heading.
- Describe *what the folder contains*, not how to use it.
- Start with the noun (what's in there), not "This folder contains…"
- Match the voice of existing abstracts:
  - `Atomic work items with status, owner, and product/app/feature context — the lowest level of the task hierarchy.`
  - `Unscoped concepts and feature ideas not yet promoted to projects or tasks — the inbox for future work.`

### 4. Write `.overview.md` (L1)

Only for folders that benefit from structural explanation (typically 3+ subfolders or with non-obvious rules). Format:

```markdown
# <folder-path> — Overview

<1–2 sentence summary of purpose and scope>

## Folder map

| Folder / File | Purpose |
|---|---|
| `subfolder/` | What it contains |
| `key-file.md` | What it is |

## Conventions

<Any naming rules, frontmatter requirements, or workflow rules specific to this folder.>
```

- Use the vault path as the heading (e.g., `# _system/chief-of-staff — Overview`)
- Only include a **Conventions** section if there are real rules to document
- Keep it under ~30 lines

### 5. Workspace submodule roots — skip internals

Each `_clients/<name>/` is a git submodule root. Do NOT descend into uninitialized submodules. If the submodule is initialized (content present), you may index it. If it's a bare pointer, skip.

Wiki and codebase app submodules inside `_clients/<name>/documentation/` or `_clients/<name>/codebase/` are also git submodule roots — skip writing context files inside them. The parent folder's `.overview.md` should mention them in its folder map.

### 6. Codebase app pointer stubs

Each app submodule in `_clients/<name>/codebase/` must have `.abstract.md` as a pointer stub redirecting to the context file in `_clients/<name>/documentation/`.

**Stub format:**
```
Context: _clients/<name>/documentation/<app>.md
```

**Discover app submodule folders at runtime:**
```bash
git submodule status | awk '{print $2}' | grep "^_clients/"
```

### 7. After writing all files

```bash
git status --short | grep -E "\.abstract\.md|\.overview\.md"
```

Report a summary table:

| Tree | Created | Updated | Skipped |
|------|---------|---------|---------|
| `_system/` | N | N | N |
| `_clients/` | N | N | N |

## Folder coverage

Folders that must have `.abstract.md` (re-run `find _system _clients -mindepth 1 -type d` at runtime — this list may be stale):

```
_system/
_system/users/
_system/chief-of-staff/
_system/chief-of-staff/references/
_system/awi/
_system/gtd/
_clients/
_clients/<name>/
_clients/<name>/agenda/
_clients/<name>/agenda/tasks/
_clients/<name>/agenda/projects/
_clients/<name>/agenda/people/
_clients/<name>/agenda/daily/
_clients/<name>/agenda/weekly/
_clients/<name>/agenda/outputs/
_clients/<name>/agenda/planning/
_clients/<name>/agenda/ideas/
_clients/<name>/agenda/user-profile-inference/
_clients/<name>/documentation/
_clients/<name>/codebase/
```

Folders that should also have `.overview.md`:

```
_system/
_system/users/
_system/chief-of-staff/
_clients/
_clients/<name>/
_clients/<name>/agenda/
_clients/<name>/documentation/
```

> Re-run `find _system _clients -mindepth 1 -type d` at the start of each execution — the list above may be stale.
