# Agentic Workflow Integrator (AWI) — Claude Code

**All vault rules, structure, taxonomy, and commands are in [INSTRUCTIONS.md](_system/INSTRUCTIONS.md).** Read it before any vault operation.

> **Do NOT modify this file for vault rules.** Update `_system/INSTRUCTIONS.md` instead — it is the single source of truth shared across all AI agents.

## Claude Code-specific

- PostToolUse hook auto-commits after Write/Edit operations on `_workspace/` and `_system/` — do NOT commit manually unless asked.
- Skills available: see `.claude/skills/` for `/today`, `/week`, `/quarter`, `/year`, `/new`, `/history`, `/delegate`, `/awi-user-create`, `/awi-user-login`, `/initialize`.
- Full file format templates: `_system/chief-of-staff/references/file-formats.md`.
- Get current date: `bash .claude/hooks/get-datetime.sh full`.

## End of Session

Before closing every session, tell the user one or more things you observed or learned about them during the conversation — ideally things they may not be consciously aware of about themselves. Then save those observations to `_workspace/guido-amici/agenda/user-profile-inference/YYYY-MM-DD - <FullName>.md` with the user's name as the H1 heading and the date in the filename.
