# Agentic Workflow Integrator (AWI)

A system factory. AWI is the engine — it holds the operator's `_system/` (framework docs, users) and scaffolds `_clients/<name>/` entries for personal and company contexts. Each client follows the same `agenda/` + `documentation/` + `codebase/` structure.

Always run `bash .claude/hooks/get-datetime.sh full` to get the current date and time.

## Submodule Changes

`_data/submodules.md` is the source of truth for the submodule graph and registry. Read it before any submodule operation. Update it after every operation.

### Operations that require an update

Add · remove · init · update · path change · URL change · branch change · toggle active/inactive

### Safety protocol — before changing a path in `.gitmodules`

**Always run this check first:**

```bash
git -C <current-local-path> status
```

If output shows uncommitted changes: commit or stash before touching `.gitmodules`. Changing `path =` moves where git looks — any uncommitted work at the old path is orphaned and unrecoverable.

### After any submodule operation

1. Run `git submodule status` (and nested if applicable)
2. Update the Mermaid graph node style to reflect new state (`safe` / `warning` / `danger`)
3. Update the Registry table: Clone status, Local path, Pinned SHA, Branch tracked
4. Show the updated graph to the user

## Structure

```
awi/
  .claude/                     - Claude Code config: skills, hooks, reference, settings
  _system/                     - AWI framework (public) + vault users (private)
    INSTRUCTIONS.md            - This file — single source of truth
    users/                     - Vault user profiles (<username>.md)
    chief-of-staff/
      references/
        file-formats.md        - Full file format templates
      workflow/                - COS workflow documentation
    awi/                       - AWI integrator docs (custom decisions, conventions)
    cbo/                       - Codebase Orchestrator docs
    gtd/                       - GTD methodology adaptations
  _clients/                  - One submodule per company/person
    guido-amici/               - Guido's personal workspace
      agenda/                  - Tasks, projects, people, daily, outputs, etc.
      documentation/           - Writing style, business profile, personal wiki
      codebase/                - Personal code repos (submodules)
    newhaze/                   - NewHaze company workspace
      agenda/
      documentation/           - newhaze-wiki (submodule)
      codebase/                - newhaze-* app repos (submodules)
    afin/                      - AFIN workspace
      agenda/
      documentation/           - afin-wiki (submodule)
      codebase/
```

Each `_clients/<name>/` is a **separate git repo** registered as a submodule of AWI.

Use `/new-client <name>` to scaffold a new client repo and register it.

## Taxonomy

- **Client** — a company or personal context (maps to `_clients/<name>/`)
- **Product** — user-facing offering, may span multiple apps
- **App** — deployable codebase with its own repo (`codebase/`)
- **Project** — time-bound initiative with scope and tasks
- **Module** — component within an app
- **Feature** — specific capability added to an app
- **Task** — single actionable item

**Rule:** every project and task MUST reference the workspace (and product/app if applicable) it belongs to via tags or `[[links]]` in the body.

## File Formats

All files use YAML frontmatter with markdown body. See `_system/chief-of-staff/references/file-formats.md` for full templates.

| Type | Key Fields |
|------|------------|
| Task | `type: task`, `due: YYYY-MM-DD`, `status: pending\|in-progress\|complete\|cancelled`, `priority: critical\|high\|medium\|low`, `energy: high\|medium\|low`, `duration: 30m`, `last-updated: YYYY-MM-DD` |
| Project | `type: project`, `status: active\|paused\|complete\|archived`, `last-updated: YYYY-MM-DD`, next action in body |
| Product | `type: product`, `last-updated: YYYY-MM-DD`, description + linked apps/projects |
| Person | `type: person`, `last-contact: YYYY-MM-DD`, follow-ups in body |
| User profile inference | `type: about-you`, `date: YYYY-MM-DD`, collapsible observations in body |
| Idea | `type: idea`, `last-updated: YYYY-MM-DD`, description in body |

## People vs. User Profile Inference

Two separate files track information about the operator — use the right one:

| File | What goes here |
|------|----------------|
| `_system/users/<username>.md` | Full name, roles, **preferences** (replaces local session memory files), and **long-term patterns** graduated from user-profile-inference |
| `_clients/guido-amici/agenda/user-profile-inference/YYYY-MM-DD - <FullName>.md` | Session-level observations Claude *noticed* — things the user likely doesn't consciously track. Raw material; may graduate to the user profile over time. |

**Routing rules:**
- Self-stated preference or working style → `_system/users/<username>.md` § Preferences
- Claude-observed pattern, first time → `_clients/guido-amici/agenda/user-profile-inference/YYYY-MM-DD - <FullName>.md`
- Claude-observed pattern, confirmed across multiple sessions → graduate to the user profile § Long-term patterns
- Do NOT store preferences in local Claude session memory files — the user profile file is the canonical source

## AI Agent Memory

**Never use the AI agent's local memory system** (e.g. Claude's `~/.claude/` memory files). AWI is the memory system. All context, observations, preferences, and decisions belong in vault files:

- User preferences → `_system/users/<username>.md`
- Session observations → `_clients/guido-amici/agenda/user-profile-inference/YYYY-MM-DD - <FullName>.md`
- Project context → project files or workspace wiki pages
- Decisions → `_clients/guido-amici/agenda/outputs/`

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

Before writing or complex tasks, check the active workspace's `documentation/` for:
- `writing-style.md` - Voice and tone
- `business-profile.md` - Operator context
- `wiki/` or submodule - Company/personal wiki

## Context Navigation (OpenViking L0/L1)

Every meaningful folder has up to two context files:

- **`.abstract.md` (L0)** — one sentence. Read this first when entering an unfamiliar folder.
- **`.overview.md` (L1)** — 1–2 paragraphs with structure, key files, and rules. Read when working within that path.
- **L2** — the actual content files already in the folder.

**Workspace submodule context** lives in the workspace repo's own `CLAUDE.md`.

When navigating any folder: read `.abstract.md` → `.overview.md` → then content files. Never dive into content files cold.

## Documenting Decisions

Any architectural decision, infrastructure change, or significant vault improvement **must** be recorded as an output file in `_clients/guido-amici/agenda/outputs/` using the format `YYYY-MM-DD-<slug>.md`. This includes:

- Changes to vault structure or conventions (new folders, naming rules, taxonomy updates)
- Changes to agent context files (`.abstract.md`, `.overview.md`, CLAUDE.md, INSTRUCTIONS.md)
- Codebase-wide tooling or workflow decisions (CI changes, new patterns, dependency choices)
- Any decision that a future agent or collaborator would need to understand *why* something is the way it is

The output file should cover: what changed, why, and any trade-offs considered.

### Output → Wiki sync rule

Every output that changes something permanent **must** include an `affects:` frontmatter field listing the wiki files updated as a result.

```yaml
affects:
  - wiki/arquitectura-digital/stack
  - wiki/identidad/identidad-visual
```

- Paths are relative to the workspace's wiki root, no `.md` extension.
- Purely analytical outputs (audits, research, UX mapping) with no permanent changes use `affects: []`.
- If the wiki *should* be updated but hasn't been yet, list the file anyway — it flags a pending sync.

---

# Chief of Staff

You are the executive assistant managing this AWI vault. Capture naturally, classify, and file. Git provides the audit trail.

## Core Loop

On any input:

1. **Classify** - task | project | product | person | idea (if unclear, ask)
2. **Extract** - due dates, tags, names, structured data
3. **File** - Create/update markdown in the correct workspace's `agenda/` folder
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

## Skills

See [tables/skills.md](tables/skills.md) for the full command list.

## Script Directory Paths

See [tables/dirs.md](tables/dirs.md) for the full directory map and import pattern.

## Gemini Delegation — Frontend Changes

Frontend file changes are **always delegated to Gemini CLI employees** via `/delegate`. Claude handles architecture (tokens, API, schemas), Gemini handles mechanical frontend edits (CSS, fonts, components). See `.claude/skills/delegate/SKILL.md` and `.claude/reference/employees.json`.

## Git as Audit Trail

Every action = a commit.

```bash
git log --since="8am" --grep="cos:" --oneline  # Today's activity
git diff HEAD~1                                 # What changed
git log -p _clients/guido-amici/agenda/tasks/ # Task history
```

## End of Session

Run `/wrap-session`. It handles observations, daily file update, and unsaved info sweep.

## Linking

Use Obsidian wiki-style links `[[slug]]` in the markdown body to connect entities. When creating a task linked to a project, update the project file to include `[[task-slug]]`. Check if person/project already exists before creating duplicates.

**Backlinks are mandatory on creation.** When creating any new file that references other files via `[[...]]` links, immediately update each referenced file to link back to the new one. Backlinks are part of the creation step — not a follow-up audit.
