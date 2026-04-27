---
type: reference
title: AWI Skills
---

# AWI Skills

When the user types `/<command>`, read and execute the skill file at `.claude/skills/<command>/SKILL.md`.

If the skill file does not exist, tell the user the command is not available.

| Command | Purpose |
|---------|---------|
| `/today` | Daily plan from due tasks and active projects |
| `/week` | Weekly plan with task scheduling |
| `/quarter` | Quarterly goals and milestones |
| `/year` | Annual strategic plan |
| `/new <text>` | Quick capture — classify and file |
| `/history` | Recent git activity |
| `/delegate <task>` | Autonomous task completion |
| `/awi-user-login <username>` | Load user profile for session |
| `/wrap-session` | End-of-session ritual |
| `/awi-introduction` | First-time onboarding — GitHub, language, preferences |
| `/awi-initialize` | Bootstrap AWI repo file structure (run once after /awi-introduction) |
| `/awi-org <name>` | Scaffold new `_data/organizations/<name>/` repo and register as submodule |
| `/awi-sync` | Sync all repos (submodules + root + awi-core dev-claude mirror) |
