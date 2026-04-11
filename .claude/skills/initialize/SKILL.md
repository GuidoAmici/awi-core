---
name: initialize
description: Scaffold a new <name>-workspace repo for a company or client. Creates the standard _agenda/ + _context/ + _codebase/ structure, initializes git, and registers the workspace in AWI. Usage: /initialize <name>
---

# /initialize — Scaffold a Workspace

Creates a new `<name>-workspace` repo with the standard AWI structure.

## Usage

```
/initialize <name>
```

Where `<name>` is the company or client slug (e.g. `newhaze`, `afin`, `guido`).

---

## Steps

### Step 1 — Get name

Check ARGUMENTS.

- **If ARGUMENTS has a value** — use it as `<name>`. Proceed to Step 2.
- **If ARGUMENTS is empty** — ask:
  ```
  What is the workspace name? (e.g. newhaze, afin, guido)
  ```
  Wait for reply. Use it as `<name>`.

---

### Step 2 — Determine target path

Ask:
```
Where should <name>-workspace be created? (default: sibling of this repo)
```

Default: parent directory of the current AWI root (i.e., `../`).

---

### Step 3 — Run the scaffold script

```bash
python3 .claude/skills/initialize/scripts/init_workspace.py <name> [path]
```

This creates:
```
<name>-workspace/
  _documentation/
    _agenda/
      tasks/   projects/   people/   ideas/
      daily/   weekly/     outputs/  planning/
      user-profile-inference/
    _context/
      users/
      codebase/
  _codebase/
  CLAUDE.md
  .gitignore
```

And runs `git init` + initial commit.

---

### Step 4 — Ask about wiki

```
Does <name> have a wiki repo? (y/n)
```

- **Yes** → ask for the GitHub URL, then:
  ```bash
  git submodule add <url> _documentation/_context/wiki
  git commit -m "cos: add wiki submodule"
  ```
- **No** → skip. Wiki can be added later with `git submodule add`.

---

### Step 5 — Register in AWI

Append to `.claude/reference/workspaces.json` (create if missing):

```json
{
  "<name>": {
    "path": "<absolute-path-to-workspace>",
    "wiki": "<wiki-url-or-null>"
  }
}
```

---

### Step 6 — Confirm

Output:
```
✓ <name>-workspace created at <path>

Structure:
  _documentation/_agenda/    ← tasks, projects, people, daily, weekly, outputs
  _documentation/_context/   ← users, codebase[, wiki]
  _codebase/                 ← app submodules go here

Next steps:
  1. cd <path>/<name>-workspace
  2. claude
  3. /awi-user-create <username>
  4. /awi-user-login <username>
```
