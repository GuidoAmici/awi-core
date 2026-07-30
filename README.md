# Agentic Workflow Integrator (AWI)

> Your AI-powered executive assistant and personal operating system

A git-tracked Obsidian vault designed for Claude Code. Natural language in, organized knowledge out. Every action creates a timestamped commit, giving you a complete audit trail of your productivity system.

---

## What It Does

**AWI** is a system factory — it serves two roles simultaneously:

1. **Personal OS** — your own agenda, planning, and daily rhythm live here
2. **Workspace factory** — use `/awi-org <name>` to spin up a self-contained org workspace repo for any company or client, with its own agenda, documentation, and codebases

Each workspace follows the same structure and is operated by the same skills. AWI is the engine that runs all of them.

**AWI** transforms Claude Code into an executive assistant that:

- **Captures naturally** — Say "meeting with Sarah Friday about Q2 planning" and watch it create linked person notes, tasks, and project files
- **Plans your day** — Aggregates due tasks, overdue items, and active projects into a daily plan
- **Reviews progress** — Compares planned vs actual at end of day, updates statuses, identifies patterns
- **Delegates work** — Forks new terminal sessions to work on tasks autonomously across repos
- **Tracks everything** — Changes are committed at logical task boundaries using [Conventional Commits with scope](_system/_agentic-workflow-integrator/references/commit-format.md), which is what makes the changelog generatable

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
git clone https://github.com/GuidoAmici/awi-core.git awi
cd awi
```

Nothing in AWI is a git submodule — everything is materialised by `git clone`
from the manifests. Run `/awi-initialize` once you are logged in and it will
clone every repo your manifest declares. See
[ADR 0009](docs/adr/0009-manifiestos-json-en-lugar-de-submodulos.md).

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

## Delegation

Work with the scope of one issue can be handed to a **delegate**: an agent
process that runs unattended, with a wall clock cap of 45 minutes.

### Agent personas

A delegate adopts an **agent persona** — a named agent definition discovered from
`_system/agency-agents/`. The agent's file is its system prompt and its place in
the tree is its category. There is no registry to configure: adding a persona
means adding a file. See
[ADR 0008](docs/adr/0008-agent-discovery-desde-agency-agents.md).

```bash
ls _system/agency-agents/            # the categories
ls _system/agency-agents/engineering # the personas in one category
```

### Dispatching

Only a **grilled issue** is eligible: one that completed a grill session, carries
`ready-for-agent`, and names its agent persona in its Agent Brief.

```
/delegate-issue
```

It lists what is eligible and confirms before firing. Each delegate keeps its
scratch outside the versioned tree, and reports back into the issue.

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
| `/awi-org <name>` | Scaffold a new org workspace repo | `/awi-org <org-name>` |
| `/wrap-session` | End-of-session ritual | `/wrap-session` |

---

## How Classification Works

When you use `/new`, the system:

1. **Decomposes** input into entities (may be multiple)
2. **Classifies** each as task, project, person, or idea
3. **Extracts** due dates, tags, names
4. **Links** entities via `[[wiki-style]]` links
5. **Writes** files to the appropriate folder under `_documentation/_agenda/`
6. **Commits** at logical task boundaries, in Conventional Commits format

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

All files use YAML frontmatter. See `_system/chief-of-staff/references/file-formats.md` for full templates.

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

### Commits

There is no hook that commits for you. The agent commits at logical task
boundaries with a clear message — not after every `Write`/`Edit`.

The format is [Conventional Commits with scope](_system/_agentic-workflow-integrator/references/commit-format.md):
`type(scope): subject`. It is not a style preference — the messages are the raw
material of `CHANGELOG.md`, which release-please generates from them.

- Filter by area: `git log --grep="^docs(newhaze)"`
- Everything but chores: `git log --invert-grep --grep="^chore"`

### Stop Sound Hook

Plays notification sound when a delegated task completes. Only triggers when `CLAUDE_DELEGATED=1` is set.

---

## Directory Structure

Every directory under `_data/` is a **separately cloned repo**, not a submodule.
There are no gitlinks anywhere: `_data/` is in `.gitignore`, which is a
correctness requirement rather than hygiene — without it, `git add -A` in the
root would swallow the children as embedded repos.

```
awi/
├── CLAUDE.md                           # Claude Code session instructions
├── CONTEXT.md                          # Domain model: what each term means
├── README.md                           # This file
│
├── _system/                            # The harness — maintained by awi-core
│   ├── _agentic-workflow-integrator/
│   │   └── INSTRUCTIONS.md             # Canonical source of truth for all agents
│   ├── chief-of-staff/                 # Operator references
│   └── agency-agents/                  # Agent personas (upstream clone, read-only)
│
├── _data/                              # Private to this operator, never committed
│   ├── users/
│   │   ├── current-user.json           # Who is logged in
│   │   └── <github-id>/                # Cloned user repo
│   │       ├── user-submodules.json    # Manifest: what this operator materialises
│   │       ├── agenda/                 # tasks/ projects/ people/ daily/ outputs/ …
│   │       └── documentation/           # professional identity, writing style
│   └── organizations/
│       └── <org-name>/                 # Cloned org workspace
│           ├── codebases.json          # Manifest: what repos the org is made of
│           ├── agenda/
│           ├── documentation/
│           └── codebase/<repo>/        # Each one a separate clone
│
├── docs/
│   ├── adr/                            # Architecture decision records
│   └── purga-del-historial.md          # Sensitive-material handling
│
└── .claude/
    ├── settings.json
    ├── rules/                          # Versioned rule sets (sensitive, vocabulary)
    ├── hooks/
    │   └── git/                        # pre-commit, post-commit
    └── skills/
        ├── new/          today/        today-start/    today-end/
        ├── week/         week-review/  quarter/        year/
        ├── history/      delegate/     wrap-session/
        ├── awi-user-create/            awi-user-login/
        └── initialize/                 # Scaffolds workspace repos
```

---

## Git as Audit Trail

Every action generates a timestamped commit:

```
type(scope): subject
```

### Useful Commands

```bash
# Today's activity
git log --since="8am" --oneline

# Last week
git log --since="7 days ago" --format="%ad %s" --date=short

# What changed last
git diff HEAD~1

# File history
git log -p <user-root>/agenda/tasks/<creation-date>-my-task.md
```

---

## Troubleshooting

### Work not being committed

There is no hook that commits for you. The agent commits at logical task boundaries; if something is left uncommitted, commit it yourself in Conventional Commits format. Ensure git commit permissions are present in `.claude/settings.json`:
```json
"allow": ["Bash(git add:*)", "Bash(git commit:*)"]
```

### Tasks not appearing in /today

1. Ensure task has `due: YYYY-MM-DD` in frontmatter
2. Check date format (ISO, no extra spaces)
3. Verify task is in `<user-root>/agenda/tasks/`

### User login not working

1. Confirm user file exists: `ls _system/users/`
2. Verify `person:` field in the user file links to a file in `<user-root>/agenda/contacts/people/`
3. Re-run `/awi-user-create <username>` if the profile is missing

---

## Design Philosophy

1. **Git is the database** — No separate storage, just markdown and commits
2. **Natural language first** — Say what you mean, let classification handle the rest
3. **Grep before glob** — Never load all files, search efficiently
4. **Progressive disclosure** — Skills load context in layers to manage tokens
5. **Commit at task boundaries** — Finished work is committed in Conventional Commits format so nothing is lost
6. **Cross-repo awareness** — Delegation maintains context across projects

---

## License

MIT License — Feel free to modify and distribute.
