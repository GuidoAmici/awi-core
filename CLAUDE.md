# Agentic Workflow Integrator (AWI) — Claude Code

**All vault rules, structure, taxonomy, and commands are in [INSTRUCTIONS.md](_system/_agentic-workflow-integrator/INSTRUCTIONS.md).** Read it before any vault operation.

> **Do NOT modify this file for vault rules.** Update `_system/_agentic-workflow-integrator/INSTRUCTIONS.md` instead — it is the single source of truth shared across all AI agents.

## Claude Code-specific

- **Always run Bash commands using relative paths** (e.g. `bash .claude/hooks/get-datetime.sh full`, not absolute paths). Working directory is the project root.
- PostToolUse hook auto-commits after Write/Edit operations on `_data/entities/` and `_system/` — do NOT commit manually unless asked.
- Skills available: see `.claude/skills/` for `/today`, `/week`, `/quarter`, `/year`, `/new`, `/history`, `/delegate`, `/awi-user`, `/awi-introduction`, `/awi-org`.
- Full file format templates: `_system/chief-of-staff/references/file-formats.md`.
- Get current date: `bash .claude/hooks/get-datetime.sh full`.

## Agent skills

### Issue tracker

GitHub Issues distributed by scope — codebase repos, org workspace repos, and `GuidoAmici/my-awi-user` for cross-org work. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Multi-context layout — `CONTEXT-MAP.md` at root points to per-org `CONTEXT.md` files under `_data/organizations/`. See `docs/agents/domain.md`.

## End of Session

Before closing every session, tell the user one or more things you observed or learned about them during the conversation — ideally things they may not be consciously aware of about themselves. Then save those observations to `<user-root>agenda/user-profile-inference/YYYY-MM-DD - <FullName>.md` with the user's name as the H1 heading and the date in the filename.
