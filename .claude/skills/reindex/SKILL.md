---
name: reindex
description: Re-index the _documentation tree and _codebase app folders by creating or updating .abstract.md (L0) and .overview.md (L1) files, following the OpenViking context navigation convention.
---

# /reindex — Documentation Tree Re-index

Walks the entire `_documentation/` tree and every app folder in `_codebase/`, ensuring all folders have accurate `.abstract.md` and `.overview.md` files per the OpenViking L0/L1 convention.

## When to run

- After renaming, moving, or restructuring folders inside `_documentation/` or `_codebase/`
- After adding new top-level sections, subfolders, or app submodules
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
find _documentation -mindepth 1 -type d | sort
```

Also check the root `_documentation/` folder itself.

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

- Use the vault path as the heading (e.g., `# _documentation/schedule — Overview`)
- Only include a **Conventions** section if there are real rules to document
- Keep it under ~30 lines

### 5. Wiki submodule roots — skip

Submodule roots under `_documentation/_context/workspaces/` (e.g. `newhaze-wiki`, `afin-wiki`) are git submodule roots. Do NOT write `.abstract.md` or `.overview.md` inside them — their own `CLAUDE.md` and `_index.md` are authoritative. The parent folder `_documentation/_context/workspaces/` should mention them in its `.overview.md` folder map.

### 6. Codebase app pointer stubs

Each app submodule in `_codebase/` must have `.abstract.md` **and** `.overview.md` as pointer stubs — one line each, redirecting to the real context file in `_documentation/_context/codebase/`.

**Stub format** (same for both files):
```
Context: _documentation/_context/codebase/<app>.md
```

**How to match a `_codebase/<folder>` to its context file:**

1. Try exact name match: `_documentation/_context/codebase/<folder>.md`
2. If no match, read the `app:` frontmatter field from each `.md` file in `_documentation/_context/codebase/` and match against the folder name
3. If still no match, skip with a warning — do not create a stub pointing to a non-existent file

Known name mismatches (verify at runtime — may change):

| `_codebase/` folder | context file |
|---|---|
| `newhaze-intern-panel` | `newhaze-inner-panel.md` |
| `newhaze-b2b-panel` | `newhaze-outer-panel.md` |

Non-app entries (`scripts/`, `supabase/`, `docker-compose.dev.yml`) — skip, no stub needed.

**Discover app folders at runtime:**
```bash
# Submodule folders only (exclude non-app dirs)
git submodule status | awk '{print $2}' | grep "^_codebase/"
```

**Update existing stubs** if they reference an old path (e.g., old `.mdn` extension or old `info/organization/context/apps/` path).

### 7. After writing all files

```bash
git status --short | grep -E "\.abstract\.md|\.overview\.md"
```

Report a summary table:

| Tree | Created | Updated | Skipped |
|------|---------|---------|---------|
| `_documentation/` | N | N | N |
| `_codebase/` stubs | N | N | N |

## Folder coverage (as of last restructure)

Folders that must have `.abstract.md`:

```
_documentation/
_documentation/_context/
_documentation/_context/codebase/
_documentation/_context/users/
_documentation/_agenda/
_documentation/_agenda/daily/
_documentation/_agenda/ideas/
_documentation/_agenda/ideas/mental-models/
_documentation/_agenda/outputs/
_documentation/_agenda/people/
_documentation/_agenda/planning/
_documentation/_agenda/products/
_documentation/_agenda/projects/
_documentation/_agenda/tasks/
_documentation/_agenda/user-profile-inference/
_documentation/_agenda/weekly/
_documentation/system/chief-of-staff/
_documentation/system/chief-of-staff/references/
```

Folders that should also have `.overview.md`:

```
_documentation/
_documentation/_context/
_documentation/_agenda/
_documentation/system/chief-of-staff/
```

> Re-run `find _documentation -mindepth 1 -type d` at the start of each execution — the list above may be stale.
