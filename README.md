# Second Brain

> Your AI-powered Second Brain and Chief of Staff

A git-tracked Obsidian vault designed for Claude Code. Natural language in, organized knowledge out. Every action creates a timestamped commit, giving you a complete audit trail of your productivity system.

---

## What It Does

**Second Brain** transforms Claude Code into an executive assistant that:

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
| **Git** | Version control (pre-installed on macOS) | - |
| **Python 3.8+** | For scripts (pre-installed on macOS) | - |

---

## Installation

### Step 1: Install Claude Code

If you don't have Claude Code installed:

```bash
# Install via npm (recommended)
npm install -g @anthropic-ai/claude-code

# Or via Homebrew
brew install claude-code
```

Verify installation:

```bash
claude --version
```

On first run, Claude Code prompts you to authenticate with your Anthropic account.

> **Prefer a GUI?** Anthropic offers a [VS Code extension](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code) with the same agentic capabilities—same power, nicer interface.

### Step 2: Install Obsidian

Download from [obsidian.md/download](https://obsidian.md/download). Obsidian is free for personal use.

### Step 3: Clone the Repository

```bash
git clone https://github.com/bradautomates/second-brain.git
cd second-brain
```

Or download the ZIP from GitHub and extract it.

### Step 4: Open as Obsidian Vault

1. Open Obsidian
2. Click **"Open folder as vault"**
3. Select the `second-brain` folder
4. Trust the folder when prompted

The `.gitignore` excludes Obsidian workspace files so your local settings won't conflict with git.

### Step 5: Configure Your Context (Recommended)

Create files in `context/` to personalize Claude's behavior:

**context/writing-style.md:**

```markdown
---
type: context
---

## Writing Style

- Concise, direct communication
- Bullet points over paragraphs
- Technical but accessible
```

**context/business-profile.md:**

```markdown
---
type: context
---

## Business Profile

- Role: [Your role]
- Company: [Your company]
- Focus areas: [Current projects]
```

Claude reads these to understand how you work and communicate.

### Step 6: Start Claude Code

```bash
cd second-brain
claude
```

The `CLAUDE.md` file provides all context automatically. You're ready to go.

### Step 7: Test It Out

```bash
# Capture something
/new remember to review quarterly report by Friday

# Generate today's plan
/today

# Check recent activity
/history
```

---

## Setting Up AI Employees (Cross-Repo Delegation)

The real power comes from delegating work to specialized AI employees.

### What Are AI Employees?

AI employees are separate Claude Code repositories with specialized skills:

- **[Head of Content](https://github.com/bradautomates/head-of-content)** — Researches winning content across social platforms

Each lives in its own repo. The Chief of Staff orchestrates all of them via tasks created in the second brain.

### Configure Employee Paths

Edit `.claude/reference/employees.json`:

```json
{
  "head-of-content": "~/Documents/GitHub/head-of-content"
}
```

### Delegate Work

```bash
/delegate head-of-content: research YouTube content for AI productivity niche
```

A separate Claude instance spawns in a new terminal, working in the employee's repo. When done:

- Task file updates with output locations
- Notification sound plays
- Full traceability of what was delegated

---

## Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `/new <text>` | Quick capture — classify and file | `/new call John about project by Friday` |
| `/today` | Generate daily plan from due tasks | `/today` |
| `/daily-review` | End of day — planned vs actual | `/daily-review` |
| `/history` | Recent git activity | `/history` |
| `/delegate <task>` | Fork terminal for autonomous work | `/delegate write the quarterly report` |

---

## How Classification Works

When you use `/new`, the system:

1. **Decomposes** input into entities (may be multiple)
2. **Classifies** each as task, project, person, or idea
3. **Extracts** due dates, tags, names
4. **Links** entities via `[[wiki-style]]` links
5. **Writes** files to appropriate folders
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

All files use YAML frontmatter:

### Task

```yaml
---
type: task
due: 2026-01-25
status: pending  # pending | in-progress | complete | cancelled
tags: [work, q1]
---
Description of what needs to be done.
```

### Project

```yaml
---
type: project
status: active  # active | paused | complete | archived
tags: [client-work]
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
---
## Context
Who they are, relationship.

## Follow-ups
- [ ] Pending items with this person
```

### Idea

```yaml
---
type: idea
tags: [product, ai]
---
Description of the idea and potential applications.
```

---

## Hooks

The system uses two hooks configured in `.claude/settings.json`:

### Auto-Commit Hook (PostToolUse)

Triggers after every `Write` or `Edit` operation on vault content:

```bash
.claude/hooks/auto-commit.sh
```

- Only commits files in: `tasks/`, `projects/`, `people/`, `ideas/`, `daily/`, `weekly/`
- Generates commit messages: `cos: new task - task-name` or `cos: update project - project-name`
- Filter all activity: `git log --grep="cos:"`

### Stop Sound Hook

Plays notification sound when delegated task completes:

```bash
.claude/hooks/stop-sound.sh
```

Only triggers when `CLAUDE_DELEGATED=1` environment variable is set.

---

## Delegation

> **Credit:** The delegate skill is based on [IndieDev Dan's](https://github.com/disler) [fork-repository-skill](https://github.com/disler/fork-repository-skill). Check out his [YouTube channel](https://www.youtube.com/@indydevdan) for more Claude Code content.

The `/delegate` command forks a new terminal window for autonomous work:

```bash
/delegate write the quarterly report based on project notes
```

### How It Works

1. Reads `employees.json` for cross-repo delegation targets
2. Builds prompt with full context (absolute paths, source repo reference)
3. Executes via `fork_terminal.py`:
   ```bash
   python3 .claude/skills/delegate/scripts/fork_terminal.py 'claude --model opus "<prompt>"'
   ```
4. New terminal opens with `CLAUDE_DELEGATED=1` set
5. When complete, `stop-sound.sh` plays notification

### Model Selection

| Variable | Model | Use Case |
|----------|-------|----------|
| `DEFAULT_MODEL` | opus | Standard delegation |
| `HEAVY_MODEL` | opus | Complex multi-step work |
| `BASE_MODEL` | sonnet | Moderate complexity |
| `FAST_MODEL` | haiku | Quick operations |

### Cross-Repo Delegation

Configure delegation targets in `.claude/reference/employees.json`:

```json
{
  "head-of-content": "~/Documents/GitHub/head-of-content"
}
```

Then delegate: `/delegate head-of-content: research competitors`

---

## Skills Reference

### `/new` — Quick Capture

Parses natural language, classifies entities, creates linked files.

**Input:** "New project with John Smith for marketing outbound, need landing page"

**Creates:**
- `people/john-smith.md` (if doesn't exist)
- `projects/marketing-outbound.md` (linked to John Smith)
- `tasks/create-landing-page.md` (linked to project)

### `/today` — Daily Planning

Generates `daily/YYYY-MM-DD.md` with:

- **Due Today** — Tasks with today's due date
- **Overdue** — Past-due tasks with days overdue
- **Active Projects** — Projects with `status: active` and their next actions
- **Recent Activity** — Today's `cos:` commits

Uses grep-first approach (never globs all tasks):

```bash
grep -l "due: 2026-01-25" tasks/*.md
```

### `/daily-review` — End of Day

Compares planned vs actual:

1. Reads daily plan
2. Gets activity from `git log --since="8am" --grep="cos:"`
3. Updates task statuses
4. Appends review section with completed/incomplete items
5. Commits: `cos: daily review for YYYY-MM-DD`

### `/history` — Recent Activity

Shows last 7 days of Chief of Staff activity:

```bash
git log --since="7 days ago" --grep="cos:" --format="%ad %s" --date=short
```

### `/delegate` — Task Delegation

Forks terminal for autonomous work. See [Delegation](#delegation) section.

### `/skill-creator` — Create New Skills

Comprehensive guide for building skills with proper structure:

```
skill-name/
├── SKILL.md           # Required: frontmatter + instructions
├── scripts/           # Executable Python/Bash
├── references/        # Documentation for context
└── assets/            # Templates, images for output
```

Initialize a new skill:

```bash
python3 .claude/skills/skill-creator/scripts/init_skill.py my-skill --path .claude/skills
```

### `/start-second-brain` — Vault Initialization

Creates folder structure and initializes git:

```bash
python3 .claude/skills/start-second-brain/scripts/init_vault.py [path]
```

---

## Git as Audit Trail

Every action generates a timestamped commit with consistent format:

```
cos: <action> - <description>
```

### Commit Types

| Pattern | Meaning |
|---------|---------|
| `cos: new task - name` | Created task |
| `cos: update project - name` | Modified project |
| `cos: complete task - name` | Marked complete |
| `cos: daily plan for YYYY-MM-DD` | Created daily note |
| `cos: daily review for YYYY-MM-DD` | End of day review |

### Useful Commands

```bash
# Today's activity
git log --since="8am" --grep="cos:" --oneline

# Last week
git log --since="7 days ago" --grep="cos:" --format="%ad %s" --date=short

# What changed last
git diff HEAD~1

# File history
git log -p tasks/my-task.md

# All Chief of Staff commits
git log --grep="cos:"
```

---

## Directory Structure

```
second-brain/
├── CLAUDE.md                           # Main project instructions
├── README.md                           # This file
├── .gitignore                          # Excludes Obsidian workspace files
├── tasks/                              # Items with due dates
├── projects/                           # Ongoing work
├── people/                             # Relationship notes
├── ideas/                              # Captured thoughts
├── context/                            # LLM context files
├── daily/                              # Daily plans (YYYY-MM-DD.md)
├── weekly/                             # Weekly summaries (YYYY-WNN.md)
├── outputs/                            # Deliverables
└── .claude/
    ├── settings.json                   # Permissions and hooks config
    ├── reference/
    │   ├── file-formats.md             # Templates for all file types
    │   └── employees.json              # Delegation targets
    ├── hooks/
    │   ├── auto-commit.sh              # Auto-commit after Write/Edit
    │   └── stop-sound.sh               # Notification on delegation complete
    └── skills/
        ├── new/SKILL.md                # Quick capture
        ├── today/SKILL.md              # Daily planning
        ├── daily-review/SKILL.md       # End of day review
        ├── history/SKILL.md            # Recent activity
        ├── delegate/                   # Task delegation
        │   ├── SKILL.md
        │   ├── scripts/fork_terminal.py
        │   └── references/fork_summary_user_prompt.md
        ├── skill-creator/              # Skill creation guide
        │   ├── SKILL.md
        │   ├── scripts/
        │   │   ├── init_skill.py
        │   │   ├── package_skill.py
        │   │   └── quick_validate.py
        │   └── references/
        │       ├── output-patterns.md
        │       ├── workflows.md
        │       └── research-skill-pattern.md
        └── start-second-brain/         # Vault initialization
            ├── SKILL.md
            └── scripts/init_vault.py
```

---

## Troubleshooting

### Auto-commit not working

1. Check permissions in `.claude/settings.json`:
   ```json
   "allow": ["Bash(git add:*)", "Bash(git commit:*)"]
   ```

2. Verify hook is executable:
   ```bash
   chmod +x .claude/hooks/auto-commit.sh
   ```

3. Confirm file is in a tracked directory (`tasks/`, `projects/`, etc.)

### Tasks not appearing in /today

1. Ensure task has `due: YYYY-MM-DD` in frontmatter
2. Check date format matches exactly (no spaces, ISO format)
3. Verify task is in `tasks/` folder

### Classification asking too many questions

Confidence threshold is 0.5. If you want less confirmation:
- Be more specific in input: "task: call John by Friday"
- Add explicit type hints

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

---

## Implement AI in Your Business

Practical AI implementation for real business results.

Learn how to implement AI tools and workflows that actually move the needle for your business on my [YouTube channel](https://www.youtube.com/@bradautomates).

Follow [@corpcowboy_](https://x.com/corpcowboy_) on X
