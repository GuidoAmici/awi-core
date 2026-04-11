# Second Brain — Claude Code

**All vault rules, structure, taxonomy, and commands are in [INSTRUCTIONS.md](INSTRUCTIONS.md).** Read it before any vault operation.

> **Do NOT modify this file for vault rules.** Update `INSTRUCTIONS.md` instead — it is the single source of truth shared across all AI agents.

## Claude Code-specific

- PostToolUse hook auto-commits after Write/Edit operations on `info/` folders — do NOT commit manually unless asked.
- Skills available: see `.claude/skills/` for `/today`, `/week`, `/quarter`, `/year`, `/new`, `/daily-review`, `/history`, `/delegate`.
- Full file format templates: `.claude/reference/file-formats.md`.
- Get current date: `powershell -c "Get-Date"`.

## End of Session

Before closing every session, tell the user one or more things you observed or learned about them during the conversation — ideally things they may not be consciously aware of about themselves. Then save those observations to `info/organization/user-profile-inference/YYYY-MM-DD.md` with the user's name as the H1 heading and the date in the filename.
