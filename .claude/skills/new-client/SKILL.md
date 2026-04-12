---
name: new-client
description: Scaffold a new client repo with agenda/, documentation/, and codebase/ structure, then register as a submodule under _clients/<name>/. Usage: /new-client <name>
---

# /new-client — Add a Client

Creates a new standalone git repo for a company or client and registers it as a submodule under `_clients/<name>/`.

## Usage

```
/new-client <name>
```

Where `<name>` is the company or client slug (e.g. `newhaze`, `afin`, `guido-amici`).

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

### Step 2 — Determine target path

Default target: `../<name>` (sibling of current AWI root).

Ask:
```
Where should the <name> repo be created? (default: ../<name>)
```

Accept the default or use the provided path.

---

### Step 3 — Run the scaffold script

```bash
python3 .claude/skills/new-client/scripts/init_client.py <name> [path]
```

This creates:
```
<name>/
  agenda/
    tasks/      projects/   people/     ideas/
    daily/      weekly/     outputs/    planning/
    user-profile-inference/
    .abstract.md
    .overview.md
  documentation/
    .abstract.md
  codebase/
  CLAUDE.md
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

### Step 5 — Register as submodule in AWI

Only if GitHub repo was created:

```bash
git submodule add https://github.com/GuidoAmici/<name>.git _clients/<name>
git commit -m "cos: add client submodule - <name>"
```

If no GitHub repo, note that submodule registration can be done later.

---

### Step 6 — Ask about wiki/documentation submodule

```
Does <name> have a wiki or documentation repo? (y/n)
```

- **Yes** → ask for the GitHub URL, then:
  ```bash
  git -C _clients/<name> submodule add <url> documentation/wiki
  git -C _clients/<name> commit -m "cos: add wiki submodule"
  ```
- **No** → skip. Can be added later.

---

### Step 7 — Confirm

Output:
```
<name> client created.

Structure:
  _clients/<name>/agenda/         ← tasks, projects, people, daily, weekly, outputs
  _clients/<name>/documentation/  ← wiki, context files
  _clients/<name>/codebase/       ← app submodules go here

Next steps:
  1. Add codebase app repos: git submodule add <url> _clients/<name>/codebase/<app>
  2. /awi-user-login <username>
```
