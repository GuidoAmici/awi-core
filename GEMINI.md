# Agentic Workflow Integrator (AWI) — Gemini CLI

**All vault rules, structure, taxonomy, and commands are in [INSTRUCTIONS.md](_system/agentic-workflow-integrator/INSTRUCTIONS.md).** Read it before any vault operation.

> **Do NOT modify this file for vault rules.** Update `_system/agentic-workflow-integrator/INSTRUCTIONS.md` instead — it is the single source of truth shared across all AI agents.

## Gemini CLI-specific

- AfterTool hook auto-commits after write_file/edit_file operations on `_clients/` and `_system/` folders — do NOT commit manually unless asked.
- Full file format templates: `_system/chief-of-staff/references/file-formats.md`.
- Get current date: `powershell -c "Get-Date"`.

## 📋 Tareas Pendientes

- [ ] **Diseñar Pipeline Agnóstico Gemini**:
  - Separar mejoras del framework (branch `dev-gemini`) de datos sensibles (`_data/`).
  - Automatizar push de entidades (`Bhunting`, `SMASH`) a sus propios repos.
  - Crear flujo para proponer mejoras base a Guido sin exponer información personal.
- [ ] **Corregir Script de Migración**: Revisar `_data/entities/SMASH/codebase/Scripts/migrate-awi-to-gemini.sh`. Actualmente falla al copiar archivos `.toml` (rutas incorrectas).
