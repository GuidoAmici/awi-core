# Agentic Workflow Integrator (AWI)

> Your AI-powered executive assistant and personal operating system

A git-tracked Obsidian vault designed for Claude Code. Natural language in, organized knowledge out. Every action creates a timestamped commit, giving you a complete audit trail of your productivity system.

---

## What It Does

**AWI** is a system factory — it serves two roles simultaneously:

1. **Personal OS** — your own agenda, planning, and daily rhythm live here
2. **Workspace factory** — use `/initialize <name>` to spin up a self-contained `<name>-workspace` repo for any company or client, with its own agenda, wiki, and codebase

Each workspace follows the same structure and is operated by the same skills. AWI is the engine that runs all of them.

**AWI** transforms Claude Code into an executive assistant that:

- **Captures naturally** — Say "meeting with Sarah Friday about Q2 planning" and watch it create linked person notes, tasks, and project files
- **Plans your day** — Aggregates due tasks, overdue items, and active projects into a daily plan
- **Reviews progress** — Compares planned vs actual at end of day, updates statuses, identifies patterns
- **Delegates work** — Forks new terminal sessions to work on tasks autonomously across repos
- **Tracks everything** — Every Write/Edit auto-commits with `cos:` prefix for easy filtering

---

## Prerequisites

| Requirement | Details | Link |
|-------------|---------|------|
| **Claude Pro/Max** | Subscription for Claude Code access | [claude.ai](https://claude.ai) |
| **Claude Code** | Anthropic's agentic CLI | [See installation below](#step-1-install-claude-code) |
| **Obsidian** | Free markdown editor (recommended) | [obsidian.md/download](https://obsidian.md/download) |
| **Git** | Version control | - |
| **Python 3.8+** | For delegation scripts | - |

---

## Installation

### Step 1: Install Claude Code

```bash
# Install via npm (recommended)
npm install -g @anthropic-ai/claude-code

# Verify
claude --version
```

On first run, Claude Code prompts you to authenticate with your Anthropic account.

> **Prefer a GUI?** Anthropic offers a [VS Code extension](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code) with the same agentic capabilities.

### Step 2: Install Obsidian

Download from [obsidian.md/download](https://obsidian.md/download). Free for personal use.

### Step 3: Clone the Repository

```bash
git clone https://github.com/GuidoAmici/awi.git
cd awi
git submodule update --init --recursive
```

### Step 4: Open as Obsidian Vault

1. Open Obsidian
2. Click **"Open folder as vault"**
3. Select the `awi` folder
4. Trust the folder when prompted

### Step 5: Launch Claude Code and Create Your User

```bash
cd awi
claude
```

Then run the user creation skill — it walks you through an interactive setup:

```
/awi-user-create <your-username>
```

You'll be asked for your full name, role, working style, and preferences. AWI uses these to tailor every session to you.

When done, log in:

```
/awi-user-login <your-username>
```

### Step 6: Test It Out

```
/new remember to review quarterly report by Friday
/today
/history
```

---

## Setting Up AI Employees (Cross-Repo Delegation)

The real power comes from delegating work to specialized AI employees.

### What Are AI Employees?

AI employees are separate Claude Code repositories with specialized skills. Each lives in its own repo. AWI orchestrates all of them via tasks created in the vault.

### Configure Employee Paths

Edit `.claude/reference/employees.json`:

```json
{
  "head-of-content": "~/Documents/GitHub/head-of-content"
}
```

### Delegate Work

```
/delegate head-of-content: research YouTube content for AI productivity niche
```

A separate Claude instance spawns in a new terminal, working in the employee's repo. When done, the task file updates with output locations and a notification plays.

---

## Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `/new <text>` | Quick capture — classify and file | `/new call John about project by Friday` |
| `/today` | Generate daily plan from due tasks | `/today` |
| `/today-start` | Morning check-in ritual | `/today-start` |
| `/today-end` | End-of-day review ritual | `/today-end` |
| `/week` | Weekly plan with task scheduling | `/week` |
| `/week-review` | Friday ritual — re-rank and plan next week | `/week-review` |
| `/quarter` | Quarterly goals and milestones | `/quarter` |
| `/year` | Annual strategic plan | `/year` |
| `/history` | Recent git activity | `/history` |
| `/delegate <task>` | Fork terminal for autonomous work | `/delegate write the quarterly report` |
| `/awi-user-create <username>` | Create a new vault user | `/awi-user-create whyto` |
| `/awi-user-login <username>` | Load user profile for session | `/awi-user-login whyto` |
| `/initialize <name>` | Scaffold a new `<name>-workspace` repo | `/initialize newhaze` |
| `/wrap-session` | End-of-session ritual | `/wrap-session` |

---

## How Classification Works

When you use `/new`, the system:

1. **Decomposes** input into entities (may be multiple)
2. **Classifies** each as task, project, person, or idea
3. **Extracts** due dates, tags, names
4. **Links** entities via `[[wiki-style]]` links
5. **Writes** files to the appropriate folder under `_documentation/_agenda/`
6. **Auto-commits** via PostToolUse hook

### Classification Rules

| Type | Trigger | Example |
|------|---------|---------|
| **Person** | Named individual with context | "Meeting with Sarah" |
| **Project** | Ongoing work, multiple steps | "Website redesign" |
| **Task** | Specific actionable item | "Call John by Friday" |
| **Idea** | Speculative, "what if" | "What if we added AI features" |

### Confidence Scoring

| Score | Action |
|-------|--------|
| **0.9+** | Proceed without confirmation |
| **0.7-0.9** | Proceed, probably correct |
| **0.5-0.7** | Proceed, note uncertainty in commit |
| **<0.5** | Ask for clarification |

---

## File Formats

All files use YAML frontmatter. See `_documentation/system/chief-of-staff/references/file-formats.md` for full templates.

### Task

```yaml
---
type: task
due: 2026-01-25
status: pending  # pending | in-progress | complete | cancelled
priority: high   # critical | high | medium | low
energy: medium   # high | medium | low
duration: 30m
tags: [work, q1]
last-updated: 2026-01-25
---
Description of what needs to be done.
```

### Project

```yaml
---
type: project
status: active  # active | paused | complete | archived
tags: [client-work]
last-updated: 2026-01-25
---
## Next Action
- First thing to do

## Notes
- Key context
```

### Person

```yaml
---
type: person
last-contact: 2026-01-20
tags: [client, design]
last-updated: 2026-01-25
---
## Roles
- Senior Designer at Acme

## Preferences
- Async communication preferred

## Long-term patterns
<!-- Graduated from user-profile-inference -->
```

---

## Hooks

The system uses hooks configured in `.claude/settings.json`:

### Auto-Commit Hook (PostToolUse)

Triggers after every `Write` or `Edit` operation on vault content:

```bash
.claude/hooks/auto-commit.sh
```

- Only commits files in `_documentation/` folders
- Generates commit messages: `cos: new task - task-name`
- Filter all activity: `git log --grep="cos:"`

### Stop Sound Hook

Plays notification sound when a delegated task completes. Only triggers when `CLAUDE_DELEGATED=1` is set.

---

## Directory Structure

### AWI (engine + personal workspace)

```
awi/
├── CLAUDE.md                           # Claude Code session instructions
├── AGENTS.md                           # Codex CLI session instructions
├── GEMINI.md                           # Gemini CLI session instructions
├── README.md                           # This file
│
├── _documentation/
│   ├── _agenda/                        # Personal agenda (private)
│   │   ├── tasks/
│   │   ├── projects/
│   │   ├── products/
│   │   ├── people/
│   │   ├── ideas/
│   │   ├── daily/
│   │   ├── weekly/
│   │   ├── planning/
│   │   ├── outputs/
│   │   └── user-profile-inference/
│   ├── _context/                       # Personal context (private)
│   │   └── users/                      # Vault user login profiles
│   └── system/                         # Workflow framework (synced to public repo)
│       └── chief-of-staff/
│           ├── references/
│           │   ├── file-formats.md
│           │   └── installation.md
│           └── workflow/
│
└── .claude/
    ├── settings.json
    ├── reference/
    │   └── employees.json
    ├── hooks/
    │   ├── auto-commit.sh
    │   └── stop-sound.sh
    └── skills/
        ├── new/          today/        today-start/    today-end/
        ├── week/         week-review/  quarter/        year/
        ├── history/      delegate/     wrap-session/
        ├── awi-user-create/            awi-user-login/
        └── initialize/                 # Scaffolds workspace repos
```

### `<name>-workspace` (company/client instance)

Created by `/initialize <name>`. Each workspace is a standalone repo:

```
newhaze-workspace/
├── CLAUDE.md                           # Points to AWI context
│
├── _documentation/
│   ├── _agenda/                        # Company agenda
│   │   ├── tasks/     projects/    outputs/
│   │   ├── people/    daily/       weekly/
│   │   └── planning/
│   └── _context/
│       ├── wiki/                       # Company wiki (submodule)
│       └── codebase/                   # App context stubs
│
└── _codebase/                          # App submodules
    ├── newhaze-api/
    ├── newhaze-learn/
    └── ...
```

---

## Git as Audit Trail

Every action generates a timestamped commit:

```
cos: <action> - <description>
```

### Useful Commands

```bash
# Today's activity
git log --since="8am" --grep="cos:" --oneline

# Last week
git log --since="7 days ago" --grep="cos:" --format="%ad %s" --date=short

# What changed last
git diff HEAD~1

# File history
git log -p _documentation/_agenda/tasks/my-task.md
```

---

## Troubleshooting

### Auto-commit not working

1. Check permissions in `.claude/settings.json`:
   ```json
   "allow": ["Bash(git add:*)", "Bash(git commit:*)"]
   ```
2. Verify hook is executable: `chmod +x .claude/hooks/auto-commit.sh`
3. Confirm file is under `_documentation/`

### Tasks not appearing in /today

1. Ensure task has `due: YYYY-MM-DD` in frontmatter
2. Check date format (ISO, no extra spaces)
3. Verify task is in `_documentation/_agenda/tasks/`

### User login not working

1. Confirm user file exists: `ls _documentation/_context/users/`
2. Verify `person:` field in the user file links to a file in `_documentation/_agenda/people/`
3. Re-run `/awi-user-create <username>` if the profile is missing

---

## Design Philosophy

1. **Git is the database** — No separate storage, just markdown and commits
2. **Natural language first** — Say what you mean, let classification handle the rest
3. **Grep before glob** — Never load all files, search efficiently
4. **Progressive disclosure** — Skills load context in layers to manage tokens
5. **Auto-commit everything** — Hooks ensure nothing is lost
6. **Cross-repo awareness** — Delegation maintains context across projects

---

## License

MIT License — Feel free to modify and distribute.
