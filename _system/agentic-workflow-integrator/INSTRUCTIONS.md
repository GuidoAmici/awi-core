# Agentic Workflow Integrator (AWI)

A system factory. AWI is the engine — it holds the operator's `_system/` (framework docs) and `_data/` (users, submodules) and scaffolds `_data/organizations/<name>/` entries for personal and company contexts. Each entity follows the same `agenda/` + `documentation/` + `codebase/` structure.

Always run `bash .claude/hooks/get-datetime.sh full` to get the current date and time.

Always use relative paths from project root for Bash commands. Before requesting permission for any command, convert absolute paths to relative — the relative version may already be permitted and avoids unnecessary permission prompts.

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
  .claude/                          - Claude Code config: skills, hooks, reference, settings
  _data/                            - Runtime data (not framework docs)
    users/                          - One submodule per user (<github-id>/)
      current-user.md               - Points to active user's folder
    entities/                       - One submodule per company/person
      <name>/
        agenda/                     - Tasks, projects, people, daily, outputs, etc.
        documentation/              - Writing style, business profile, personal wiki
        codebase/                   - Code repos (submodules)
    submodules.md                   - Submodule graph and registry
  _system/                          - AWI framework (public)
    agentic-workflow-integrator/
      INSTRUCTIONS.md               - This file — single source of truth
      definitions.md                - Taxonomy definitions
      routing-rules.md              - Memory routing: people vs user-profile-inference
      confidence-scoring.md         - Classification confidence rubric
      navigation-patterns.md        - OpenViking L0/L1 context navigation
      references/
        wiki-links.md               - Obsidian wiki-link conventions + backlink rules
        commit-format.md            - Commit message format
        git-audit-commands.md       - Git audit trail commands
    chief-of-staff/
      references/
        file-formats.md             - Full file format templates
      workflow/                     - COS workflow documentation
```

Each `_data/organizations/<name>/` is a **separate git repo** registered as a submodule of AWI.

Use `/new-client <name>` to scaffold a new client repo and register it.

## Taxonomy

See [definitions.md](definitions.md) for the full taxonomy.

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

## Path Resolution

**`<user-root>`** — resolved at runtime by reading `_data/users/current-user.md` → `user:` field (e.g. `_data/users/42481462/`). All user agenda paths derive from this.

**`<agenda-base>`** = `<user-root>agenda/`

**Active client** — for operations targeting a company workspace (`_data/organizations/<name>/`): infer from conversation context, or ask if ambiguous. Multiple clients may be active simultaneously.

### Directory Path Constants

**Single source of truth: `.claude/skills/shared/scripts/paths.py`**

All AWI directory paths are declared there. When a directory moves, update `paths.py` only — nothing else.

**Rules:**

- **Python scripts** — must import from `paths.py`, never hardcode path strings. Add `sys.path.insert` to reach `shared/scripts/` from any location.
- **Markdown skill files** — must reference the constant name from `paths.py` (e.g. `ORGANIZATIONS_RELDIR`) when describing a path, never write the raw string. This ensures that if a path moves, the instruction stays semantically correct and the reader knows where to look for the real value.

## Memory & Routing

See [routing-rules.md](routing-rules.md) for people vs. user-profile-inference routing and AI agent memory rules.

## Links & Navigation

See [references/wiki-links.md](references/wiki-links.md) for Obsidian link conventions and backlink requirements.

See [navigation-patterns.md](navigation-patterns.md) for OpenViking L0/L1 context navigation pattern.

## Documenting Decisions

Any architectural decision, infrastructure change, or significant vault improvement **must** be recorded as an output file in `<user-root>agenda/outputs/` using the format `YYYY-MM-DD-<slug>.md`. This includes:

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

See [confidence-scoring.md](confidence-scoring.md).

## Commit Format

See [references/commit-format.md](references/commit-format.md).

## Skills

See [tables/skills.md](tables/skills.md) for the full command list.

## Script Directory Paths

See [Path Resolution → Directory Path Constants](#directory-path-constants) above and `.claude/skills/shared/scripts/paths.py` for the full directory map and import pattern.

## Git as Audit Trail

See [references/git-audit-commands.md](references/git-audit-commands.md).

## End of Session

Run `/wrap-session`. It handles observations, daily file update, and unsaved info sweep.
