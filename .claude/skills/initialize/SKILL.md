---
name: initialize
description: Initialize a new AWI (Agentic Workflow Integrator) vault with the standard folder structure and git tracking. Use when setting up a new vault from scratch.
---

# Initialize AWI Vault

Scaffold a fresh Agentic Workflow Integrator vault with the full `_documentation/` structure and git tracking.

## Usage

Run from the vault's root directory:

```bash
python3 .claude/skills/initialize/scripts/init_vault.py [path]
```

- `path` - Target directory (default: current directory)

## What It Creates

```
_documentation/
  _schedule/
    tasks/       - Items with due dates
    projects/    - Ongoing work with next actions
    people/      - Relationship notes
    ideas/       - Captured thoughts
    daily/       - Daily plans
    weekly/      - Weekly summaries
    outputs/     - Deliverables linked from source files
    planning/    - Quarterly and annual plans
    user-profile-inference/  - Session observations about the user
  _context/
    users/       - Vault user login profiles
    codebase/    - Per-app context stubs
```

Plus `.gitignore` for Obsidian files and an initial git commit.

## After Initialization

1. Create your user: `/awi-user-create <username>`
2. Log in: `/awi-user-login <username>`
3. Start working: `/today`, `/new <text>`, `/week`
