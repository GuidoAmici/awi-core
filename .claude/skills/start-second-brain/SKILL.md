---
name: start-second-brain
description: Initialize a new Second Brain vault with the standard folder structure and git tracking. Use when setting up a new vault or helping someone get started with the Second Brain system.
---

# Start Second Brain

Initialize a git-tracked Obsidian vault with the standard folder structure.

## Usage

Run from the skill's base directory:

```bash
python3 .claude/skills/start-second-brain/scripts/init_vault.py [path]
```

- `path` - Target directory (default: current directory)

## What It Creates

```
info/tasks/      - Items with due dates
info/projects/   - Ongoing work with next actions
info/people/     - Relationship notes
info/ideas/      - Captured thoughts
info/context/    - LLM context files
info/daily/      - Daily plans
info/weekly/     - Weekly summaries
info/outputs/    - Deliverables linked from source files
```

Plus `.gitignore` for Obsidian files and an initial git commit.
