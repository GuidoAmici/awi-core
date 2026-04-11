# Agentic Workflow Integrator (AWI) — Gemini CLI

**All vault rules, structure, taxonomy, and commands are in [INSTRUCTIONS.md](system/INSTRUCTIONS.md).** Read it before any vault operation.

> **Do NOT modify this file for vault rules.** Update `system/INSTRUCTIONS.md` instead — it is the single source of truth shared across all AI agents.

## Gemini CLI-specific

- AfterTool hook auto-commits after write_file/edit_file operations on `_documentation/` folders — do NOT commit manually unless asked.
- Full file format templates: `.claude/reference/file-formats.md`.
- Get current date: `powershell -c "Get-Date"`.
