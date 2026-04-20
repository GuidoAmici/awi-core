---
name: awi-client
description: Add a client to AWI — create from scratch or import an existing GitHub repo. Scaffolds agenda/, documentation/, codebase/ structure and registers as submodule under _data/organizations/<name>/. Usage: /awi-client <name>
---

# /awi-client — Add a Client

Adds a client workspace under `_data/organizations/<name>/` — either scaffolded fresh or imported from an existing GitHub repo.

## Usage

```
/awi-client <name>
```

---

## Steps

### Step 1 — Get name

Check ARGUMENTS.

- **If ARGUMENTS has a value** — use it as `<name>`. Proceed to Step 2.
- **If ARGUMENTS is empty** — ask:
  ```
  What is the client name? (e.g. newhaze, afin, acme-corp)
  ```
  Wait for reply. Use it as `<name>`.

---

### Step 2 — Choose mode

Ask:

```
Create from scratch or import from GitHub?
  1. New — scaffold empty AWI structure, create GitHub repo
  2. Import — clone existing GitHub repo, scaffold any missing AWI structure
```

Wait for reply (`1` or `2`).

---

## Mode A — New client (choice: 1)

### A1 — Scaffold

```bash
python3 .claude/skills/awi-client/scripts/init_client.py <name>
```

Creates under `_data/organizations/<name>/`:
```
agenda/
  tasks/   projects/  people/   ideas/
  daily/   weekly/    outputs/  planning/
  user-profile-inference/
  .abstract.md   .overview.md
documentation/
  .abstract.md
codebase/
CLAUDE.md
.gitignore
```

Runs `git init` + initial commit inside the new repo.

### A2 — Create GitHub repo

Ask:
```
Create a GitHub repo for <name>? (y/n)
```

- **Yes** →
  ```bash
  gh repo create GuidoAmici/<name> --private --description "<name> workspace"
  git -C _data/organizations/<name> remote add origin https://github.com/GuidoAmici/<name>.git
  git -C _data/organizations/<name> push -u origin main
  ```
- **No** → skip. Submodule registration will be skipped too (needs remote URL).

### A3 — Register as submodule

Only if GitHub repo was created:

```bash
git submodule add --force https://github.com/GuidoAmici/<name>.git _data/organizations/<name>
git commit -m "cos: add client submodule - <name>"
```

---

## Mode B — Import from GitHub (choice: 2)

### B1 — Get repo URL

Ask:
```
GitHub repo URL for <name>? (e.g. https://github.com/GuidoAmici/acme-corp)
```

Wait for reply. Use as `<url>`.

If `<name>` cannot be confirmed from the URL, ask:
```
Use "<name>" as the local folder name? (y / enter different name)
```

### B2 — Add as submodule

```bash
git submodule add <url> _data/organizations/<name>
git submodule update --init _data/organizations/<name>
```

### B3 — Scaffold missing AWI structure

```bash
python3 .claude/skills/awi-client/scripts/import_client.py <name>
```

Checks for missing AWI folders/files under `_data/organizations/<name>/` and creates only what's absent — never overwrites existing content. Commits additions if anything was created.

---

## Step 3 — Confirm

Output:

```
<name> client ready.

  _data/organizations/<name>/agenda/         ← tasks, projects, people, daily, weekly, outputs
  _data/organizations/<name>/documentation/  ← context files, topic folders
  _data/organizations/<name>/codebase/       ← app submodules go here

Next steps:
  - Add codebase repos: git submodule add <url> _data/organizations/<name>/codebase/<app>
  - /awi-user-login <username>
```

---

## Logging

```bash
python3 .claude/skills/shared/scripts/log_command.py awi-client <outcome>
```

`<outcome>`: `completed` | `skipped` | `errored`
