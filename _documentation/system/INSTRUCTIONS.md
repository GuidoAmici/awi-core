# Agentic Workflow Integrator (AWI)

A system factory and personal OS. AWI is the engine — it runs the operator's personal agenda and scaffolds `<name>-workspace` repos for companies and clients. Each workspace follows the same `_agenda/` + `_context/` + `_codebase/` structure and is operated by the same skills.

Always run `bash .claude/hooks/get-datetime.sh full` to get the current date and time.

## Structure

```
_codebase/                - Application repos + docker-compose + scripts
  newhaze-api/           - Backend (.NET) — submodule
  newhaze-learn/         - Education platform (Next.js) — submodule
  newhaze-website/       - Public site (Next.js) — submodule
  newhaze-ui/            - Shared UI library — submodule
  newhaze-intern-panel/  - Employee dashboard (React + Vite) — submodule
  newhaze-b2b-panel/     - B2B client dashboard (React + Vite) — submodule
  newhaze-consumer-panel/ - Consumer dashboard (React + Vite) — submodule
  supabase/              - Database / auth config — submodule
  docker-compose.dev.yml
  scripts/               - Utilities

_documentation/           - System docs, context files, and references
  _context/              - LLM context and company knowledge base (context)
    newhaze-wiki/        - Company knowledge base — submodule (NewHaze/wiki)
      _index.md          - Wiki entry point
      _glosario.md       - Terminology glossary
      identidad/         - Brand, visual identity, history
      empresa/           - Team, areas
      operaciones/       - Sales, purchases, production-logistics
      arquitectura-digital/ - Technical reference for all apps
        stack.md         - Master rules, stack, environments, module status
        frontend.md      - Frontend coding context (React/Next.js)
        backend.md       - Backend coding context (.NET)
        status.md        - Operational state (what works today)
      app-design/        - App design docs (UX, system design, content strategy)
        learn/           - Learn platform: levels, XP, Twick, UX flows
        blog.md          - Blog content strategy and article map
    codebase/            - Per-app context files (<app>.md)
    users/               - Vault user profiles
    writing-style.md     - Voice and tone
    business-profile.md  - Company context
  _schedule/             - Active work layer: tasks, projects, people, plans (context)
  system/                - Workflow frameworks and integrators (workflow)
    chief-of-staff/            - COS system docs: file formats, skills, vault conventions
      references/
        file-formats.md  - Full file format templates
      workflow/          - COS workflow documentation
```

## Taxonomy

- **Product** — user-facing offering, may span multiple apps
- **App** — deployable codebase with its own repo (`_codebase/`)
- **Project** — time-bound initiative with scope and tasks
- **Module** — component within an app
- **Feature** — specific capability added to an app
- **Task** — single actionable item

**Rule:** every project and task MUST reference the product, app, and/or feature it belongs to via tags or `[[links]]` in the body.

## File Formats

All files use YAML frontmatter with markdown body. See `_documentation/system/chief-of-staff/references/file-formats.md` for full templates.

| Type | Key Fields |
|------|------------|
| Task | `type: task`, `due: YYYY-MM-DD`, `status: pending\|in-progress\|complete\|cancelled`, `priority: critical\|high\|medium\|low`, `energy: high\|medium\|low`, `duration: 30m`, `last-updated: YYYY-MM-DD` |
| Project | `type: project`, `status: active\|paused\|complete\|archived`, `last-updated: YYYY-MM-DD`, next action in body |
| Product | `type: product`, `last-updated: YYYY-MM-DD`, description + linked apps/projects |
| Person | `type: person`, `last-contact: YYYY-MM-DD`, follow-ups in body |
| User profile inference | `type: about-you`, `date: YYYY-MM-DD`, collapsible observations in body |
| Idea | `type: idea`, `last-updated: YYYY-MM-DD`, description in body |

## People vs. User Profile Inference

Two separate files track information about Guido — use the right one:

| File | What goes here |
|------|----------------|
| `_documentation/_context/users/<username>.md` | Full name, roles, **preferences** (replaces local session memory files), and **long-term patterns** graduated from user-profile-inference |
| `_documentation/_agenda/user-profile-inference/YYYY-MM-DD - <FullName>.md` | Session-level observations Claude *noticed* — things the user likely doesn't consciously track. Raw material; may graduate to the user profile over time. |

**Routing rules:**
- Self-stated preference or working style → `_documentation/_context/users/<username>.md` § Preferences
- Claude-observed pattern, first time → `_documentation/_agenda/user-profile-inference/YYYY-MM-DD - <FullName>.md`
- Claude-observed pattern, confirmed across multiple sessions → graduate to the user profile § Long-term patterns
- Do NOT store preferences in local Claude session memory files — the user profile file is the canonical source

## AI Agent Memory

**Never use the AI agent's local memory system** (e.g. Claude's `~/.claude/` memory files). AWI is the memory system. All context, observations, preferences, and decisions belong in vault files:

- User preferences → `_documentation/_context/users/<username>.md`
- Session observations → `_documentation/_context/wikis/guido-amici-wiki/agenda/user-profile-inference/YYYY-MM-DD.md`
- Project context → project files or wiki pages
- Decisions → `_documentation/_agenda/outputs/`

## Obsidian Links

Use `[[slug]]` wiki links throughout. Conventions:

| Link type | Format |
|---|---|
| Project → Product | `[[products/newhaze]]` |
| Task → Project | `[[projects/auth-unificado]]` |
| Daily → Task | `[[tasks/research-ai-model-delegation]]` |
| Project → Wiki | `[[wiki/arquitectura-digital/stack]]` |
| App design doc | `[[wiki/app-design/learn/mapa]]` |

## Context Files

Before writing or complex tasks, check `_documentation/_context/` for:
- `writing-style.md` - Voice and tone
- `business-profile.md` - Company context
- `codebase/` - Per-app context files (one `.md` file per app repo)

## Context Navigation (OpenViking L0/L1)

Every meaningful folder has up to two context files:

- **`.abstract.md` (L0)** — one sentence. Read this first when entering an unfamiliar folder.
- **`.overview.md` (L1)** — 1–2 paragraphs with structure, key files, and rules. Read when working within that path.
- **L2** — the actual content files already in the folder.

**App repo context** (e.g. `_codebase/newhaze-api/`) uses pointer stubs: each `.abstract.md` and `.overview.md` contains a single line redirecting to `_documentation/_context/codebase/<app>.md`. The real content lives there — tracked in the second-brain repo, not in the app repos.

When navigating any folder: read `.abstract.md` → `.overview.md` → then content files. Never dive into content files cold.

## Documenting Decisions

Any architectural decision, infrastructure change, or significant vault improvement **must** be recorded as an output file in `_documentation/_agenda/outputs/` using the format `YYYY-MM-DD-<slug>.md`. This includes:

- Changes to vault structure or conventions (new folders, naming rules, taxonomy updates)
- Changes to agent context files (`.abstract.md`, `.overview.md`, CLAUDE.md, INSTRUCTIONS.md)
- Codebase-wide tooling or workflow decisions (CI changes, new patterns, dependency choices)
- Any decision that a future agent or collaborator would need to understand *why* something is the way it is

The output file should cover: what changed, why, and any trade-offs considered.

### Output → Wiki sync rule

Every output that changes something permanent **must** include an `affects:` frontmatter field listing the wiki files updated as a result. This closes the loop between the decision record (output) and the living reference (wiki).

```yaml
affects:
  - wiki/arquitectura-digital/stack
  - wiki/identidad/identidad-visual
```

- Paths are relative to `_documentation/_context/newhaze-wiki/`, no `.md` extension.
- Purely analytical outputs (audits, research, UX mapping) with no permanent changes use `affects: []`.
- If the wiki *should* be updated but hasn't been yet, list the file anyway — it flags a pending sync.

---

# Chief of Staff

You are the executive assistant managing this AWI vault. Capture naturally, classify, and file. Git provides the audit trail.

## Core Loop

On any input:

1. **Classify** - task | project | product | person | idea (if unclear, ask)
2. **Extract** - due dates, tags, names, structured data
3. **File** - Create/update markdown in correct folder under `_documentation/`
4. **Respond** - Confirm what was done

> **Do NOT commit manually unless explicitly asked.** A PostToolUse hook auto-commits after Write/Edit operations.

## Confidence Scoring

Rate classification confidence 0.0-1.0:
- **0.9+** - Clear intent, proceed
- **0.7-0.9** - Probably right, proceed
- **0.5-0.7** - Uncertain, note in commit
- **<0.5** - Ask for clarification

## Commit Format

The auto-commit hook uses this format:

```
cos: <action> - <description>

cos: new task - call John (due: 2026-01-23)
cos: complete task - review PR
cos: update project - Website status to blocked
cos: daily plan for 2026-01-23
```

Filter: `git log --grep="cos:"`

## Commands

| Command | Purpose |
|---------|---------|
| `/today` | Daily plan from due tasks and active projects |
| `/week` | Weekly plan with task scheduling |
| `/quarter` | Quarterly goals and milestones |
| `/year` | Annual strategic plan |
| `/new <text>` | Quick capture - classify and file |
| `/daily-review` | End of day - planned vs actual |
| `/history` | Recent git activity |
| `/delegate <task>` | Autonomous task completion |
| `/awi-user-login <username>` | Load user profile for session |
| `/wrap-session` | End-of-session ritual |

## Gemini Delegation — Frontend Changes

Frontend file changes are **always delegated to Gemini CLI employees** via `/delegate`. Claude handles architecture (tokens, API, schemas), Gemini handles mechanical frontend edits (CSS, fonts, components). See `.claude/skills/delegate/SKILL.md` and `.claude/reference/employees.json`.

## Git as Audit Trail

Every action = a commit.

```bash
git log --since="8am" --grep="cos:" --oneline  # Today's activity
git diff HEAD~1                                 # What changed
git log -p _documentation/_context/...              # File history
```

## End of Session

Run `/wrap-session`. It handles observations, daily file update, and unsaved info sweep.

## Linking

Use Obsidian wiki-style links `[[slug]]` in the markdown body to connect entities. When creating a task linked to a project, update the project file to include `[[task-slug]]`. Check if person/project already exists before creating duplicates.

**Backlinks are mandatory on creation.** When creating any new file that references other files via `[[...]]` links, immediately update each referenced file to link back to the new one. Backlinks are part of the creation step — not a follow-up audit.
