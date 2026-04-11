# Installation & Setup

## Prerequisites

| Requirement | Details | Link |
|-------------|---------|------|
| **Claude Pro/Max** | Subscription for Claude Code access | [claude.ai](https://claude.ai) |
| **Claude Code** | Anthropic's agentic CLI | [See Step 1 below](#step-1-install-claude-code) |
| **Obsidian** | Free markdown editor (recommended) | [obsidian.md/download](https://obsidian.md/download) |
| **Git** | Version control | - |
| **Python 3.8+** | For delegation scripts | - |

---

## Step 1: Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
claude --version
```

> Also available as a [VS Code extension](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code).

## Step 2: Install Obsidian

Download from [obsidian.md/download](https://obsidian.md/download). Free for personal use.

## Step 3: Clone the Repository

```bash
git clone https://github.com/GuidoAmici/awi.git
cd awi
git submodule update --init --recursive
```

## Step 4: Open as Obsidian Vault

1. Open Obsidian → **Open folder as vault**
2. Select the `awi` folder
3. Trust the folder when prompted

## Step 5: Launch Claude Code and Create Your User

```bash
cd awi
claude
```

Then run:
```
/awi-user-create <your-username>
```

Follow the interactive prompts (full name, role, working style, preferences). When done:

```
/awi-user-login <your-username>
```

## Step 6: Configure Your Context (Optional)

Create or edit files in `_documentation/_context/`:

**`writing-style.md`:**
```markdown
---
type: context
---
## Writing Style
- Concise, direct communication
- Bullet points over paragraphs
```

**`business-profile.md`:**
```markdown
---
type: context
---
## Business Profile
- Role: [Your role]
- Company: [Your company]
- Focus areas: [Current projects]
```

---

## Directory Structure

```
awi/
├── CLAUDE.md                        # Claude Code session instructions
├── AGENTS.md                        # Codex CLI session instructions
├── GEMINI.md                        # Gemini CLI session instructions
├── README.md                        # Project overview
├── .gitignore
│
├── system/                          # Workflow frameworks (synced to public repo)
│   └── chief-of-staff/
│       └── references/
│           ├── file-formats.md
│           └── installation.md      # This file
│
├── users/                           # Vault user login profiles
│
├── _documentation/
│   ├── _agenda/                     # Personal agenda (private)
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
│   └── _context/                    # LLM context (private)
│       ├── writing-style.md
│       ├── business-profile.md
│       └── workspaces/              # Wiki submodules
│
├── _codebase/                       # Application repos (submodules)
│
└── .claude/
    ├── settings.json                # Permissions and hooks config
    ├── reference/
    │   └── employees.json           # Delegation targets
    ├── hooks/
    │   ├── auto-commit.sh
    │   └── stop-sound.sh
    └── skills/
        ├── new/
        ├── today/
        ├── week/
        ├── quarter/
        ├── year/
        ├── history/
        ├── delegate/
        ├── wrap-session/
        ├── awi-user-create/
        ├── awi-user-login/
        └── initialize/
```
