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
git clone https://github.com/GuidoAmici/second-brain.git
cd second-brain
git submodule update --init --recursive
```

## Step 4: Open as Obsidian Vault

1. Open Obsidian → **Open folder as vault**
2. Select the `second-brain` folder
3. Trust the folder when prompted

## Step 5: Configure Your Context

Create or edit files in `_documents/organization/context/`:

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

## Step 6: Start Claude Code

```bash
cd second-brain
claude
/login-second-brain <your-username>
```

---

## Directory Structure

```
second-brain/
├── CLAUDE.md                        # Claude Code session instructions
├── INSTRUCTIONS.md                  # Full vault rules and Chief of Staff config
├── README.md                        # Project overview
├── .gitignore
│
├── _documents/                      # All vault data
│   ├── second-brain-core/
│   │   └── references/              # System documentation
│   │       ├── file-formats.md
│   │       ├── commands.md
│   │       ├── classification.md
│   │       ├── hooks.md
│   │       ├── delegation.md
│   │       ├── git-audit-trail.md
│   │       ├── design-philosophy.md
│   │       ├── installation.md
│   │       └── troubleshooting.md
│   └── organization/                # User-generated content
│       ├── newhaze-wiki/            # Company knowledge base (submodule)
│       ├── tasks/
│       ├── projects/
│       ├── products/
│       ├── people/
│       ├── ideas/
│       ├── daily/
│       ├── weekly/
│       ├── planning/
│       ├── outputs/
│       ├── context/
│       └── user-profile-inference/
│
├── _codebase/                       # Application repos (submodules)
│   ├── newhaze-api/
│   ├── newhaze-learn/
│   ├── newhaze-website/
│   ├── newhaze-intern-panel/
│   ├── newhaze-b2b-panel/
│   ├── newhaze-consumer-panel/
│   ├── newhaze-ui/
│   └── supabase/
│
└── .claude/
    ├── settings.json                # Permissions and hooks config
    ├── reference/
    │   └── employees.json           # Delegation targets
    ├── hooks/
    │   ├── auto-commit.sh
    │   ├── auto-commit.ps1
    │   ├── stop-sound.sh
    │   └── check-delegates.sh
    └── skills/
        ├── new/
        ├── today/
        ├── week/
        ├── quarter/
        ├── year/
        ├── daily-review/
        ├── history/
        ├── delegate/
        ├── login-second-brain/
        ├── wrap-session/
        └── start-second-brain/
```
