---
name: initialize
description: Scaffold a new workspace repo for a company or client. Creates a separate git repo with agenda/, documentation/, and codebase/ structure, then registers it in the manifest under _data/organizations/<name>/. Usage: /initialize <name>
---

# /initialize — Scaffold a Workspace

Creates a new standalone git repo for a company or client and registers it in the manifest under `_workspace/<name>/`.

## Usage

```
/initialize <name>
```

Where `<name>` is the company or client slug (e.g. `newhaze`, `afin`, `guido-amici`).

---

## Steps

### Step 1 — Get name

Check ARGUMENTS.

- **If ARGUMENTS has a value** — use it as `<name>`. Proceed to Step 2.
- **If ARGUMENTS is empty** — ask:
  ```
  What is the workspace name? (e.g. newhaze, afin, guido-amici)
  ```
  Wait for reply. Use it as `<name>`.

---

### Step 2 — Determine target path

The new repo is created on GitHub, then cloned into place and declared in the manifest.

Default target: `../<name>` (sibling of current AWI root).

Ask:
```
Where should the <name> repo be created? (default: ../<name>)
```

Accept the default or use the provided path.

---

### Step 3 — Run the scaffold script

```bash
python3 .claude/skills/initialize/scripts/init_workspace.py <name> [path]
```

This creates:
```
<name>/
  agenda/
    tasks/   projects/   people/   ideas/
    daily/   weekly/     outputs/  planning/
    user-profile-inference/
  documentation/
  codebase/
  .gitignore
```

And runs `git init` + initial commit.

---

### Step 4 — Create GitHub repo

Ask:
```
Should I create a GitHub repo for <name>? (y/n)
```

- **Yes** →
  ```bash
  gh repo create GuidoAmici/<name> --private --description "<name> workspace"
  git -C ../<name> remote add origin https://github.com/GuidoAmici/<name>.git
  git -C ../<name> push -u origin main
  ```
- **No** → skip. Can be done later.

---

### Step 5 — Register in the manifest and materialise

```bash
git clone https://github.com/GuidoAmici/<name>.git _data/organizations/<name>
```

Y agregar la entrada a `user-submodules.json` con su `url`, `path` y `branch`.

If no GitHub repo was created, skip this step and note that the submodule registration can be done later once the repo is published.

---

### Step 6 — Ask about the wiki/documentation repo

```
Does <name> have a wiki or documentation repo? (y/n)
```

- **Yes** → ask for the GitHub URL, then:
  ```bash
  git clone <url> _data/organizations/<name>/documentation/wiki
  Then declare it in the org's `codebases.json`.
  ```
- **No** → skip. Can be added later.

---

### Step 7 — Confirm

Output:
```
✓ <name> workspace created

Structure:
  _workspace/<name>/agenda/         ← tasks, projects, people, daily, weekly, outputs
  _workspace/<name>/documentation/  ← wiki, context files
  _data/organizations/<name>/codebase/  ← each codebase is cloned here

Next steps:
  1. Add codebase repos: declare them in the org's `codebases.json`, then clone them into `_data/organizations/<name>/codebase/<app>`
  2. /awi-user-login <username>
```
