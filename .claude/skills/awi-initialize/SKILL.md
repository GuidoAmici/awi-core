---
name: awi-initialize
description: Scaffold the AWI repo file structure for the first time. Creates _system/, _clients/, CLAUDE.md, .gitignore, and initial git commit. Run after /awi-introduction. Usage: /awi-initialize
---

# /awi-initialize — Bootstrap AWI Repo

Sets up the AWI file structure from scratch. Run this once, in a fresh empty directory, after completing `/awi-introduction`.

## Usage

```
/awi-initialize
```

No arguments needed.

---

## Steps

### Step 1 — Verify location

Check that we are not already inside an initialized AWI repo:

```bash
ls _system/ _clients/ 2>/dev/null
```

If either directory exists, stop and say:
```
This directory already has an AWI structure. Nothing to do.
Run /new-client <name> to add a client, or /awi-introduction to configure your profile.
```

---

### Step 2 — Run the bootstrap script

```bash
python3 .claude/skills/awi-initialize/scripts/init_awi.py
```

This creates:
```
./
  _system/
    users/
    chief-of-staff/
      references/
    getting-things-done/
    agentic-workflow-integrator/
  _clients/
    .abstract.md
  CLAUDE.md
  .gitignore
```

And runs `git init` + initial commit.

---

### Step 3 — Confirm

Output:
```
AWI initialized.

Structure:
  _system/     ← framework docs, user profiles
  _clients/    ← client repos go here (one submodule each)

Next steps:
  1. /new-client <name>   — add your first client
  2. /awi-user-create <username>   — create a user profile if not done yet
```

---

## Logging

At the end of this skill — regardless of outcome — log the invocation:

```bash
python3 .claude/skills/shared/scripts/log_command.py awi-initialize <outcome>
```

`<outcome>`: `completed` | `skipped` | `errored`
