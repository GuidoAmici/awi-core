# Agentic Workflow Integrator (AWI) — Codex CLI

**All vault rules, structure, taxonomy, and commands are in [INSTRUCTIONS.md](_system/INSTRUCTIONS.md).** Read it before any vault operation.

> **Do NOT modify this file for vault rules.** Update `_system/INSTRUCTIONS.md` instead — it is the single source of truth shared across all AI agents.

## Codex CLI-specific

- Codex has no post-tool hook. You MUST commit explicitly after every write to `_documentation/` folders:
  ```bash
  git add <file> && git commit -m "cos: <action> - <description>"
  ```
- Full file format templates: `.claude/reference/file-formats.md`.
- Get current date: `powershell -c "Get-Date"`.
