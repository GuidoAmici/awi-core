# Agentic Workflow Integrator (AWI) — Gemini CLI

**All vault rules, structure, taxonomy, and commands are in [INSTRUCTIONS.md](_system/_agentic-workflow-integrator/INSTRUCTIONS.md).** Read it before any vault operation.

> **Do NOT modify this file for vault rules.** Update `_system/_agentic-workflow-integrator/INSTRUCTIONS.md` instead — it is the single source of truth shared across all AI agents.

## Gemini CLI-specific

- No auto-commit hook: commit your own work at logical task boundaries with a clear `cos:` message (not after every write_file/edit_file). Don't leave finished work uncommitted.
- Full file format templates: `_system/chief-of-staff/references/file-formats.md`.
- Get current date: `powershell -c "Get-Date"`.
