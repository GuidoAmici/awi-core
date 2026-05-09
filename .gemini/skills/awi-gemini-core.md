# Skill: AWI Gemini Core (dev-gemini)

Este skill habilita el funcionamiento nativo de AWI utilizando la IA de Gemini, manteniendo paridad total con la experiencia de Claude Code.

## 🎯 Objetivo
Traducir y adaptar el workflow de AWI (Chief of Staff) para ser operado eficientemente desde Gemini CLI.

## 🛡️ Mandatos de Operación
1. **Audit Trail Nativo**: Cada operación de escritura debe disparar un commit con el prefijo `cos: gemini`.
2. **Contexto Dinámico**: Al iniciar una sesión, Gemini debe leer `GEMINI.md` y `_system/agentic-workflow-integrator/INSTRUCTIONS.md`.
3. **Resiliencia en WSL**: Usar siempre los hooks en `.gemini/hooks/` que soportan fallback de audio a través de PowerShell.

## ⌨️ Traducción de Comandos (Conceptos)
Para que el usuario no sienta diferencia, Gemini debe interpretar las intenciones de AWI:
- `/new` -> Invocación de lógica de clasificación de entidades en `_data/entities/`.
- `/today` -> Generación de resumen diario basado en `grep` de archivos `.md` con fecha actual.
- `/history` -> `git log --grep="cos:" -n 5`.

## 📂 Estructura de Referencia
- **Hooks**: `.gemini/hooks/auto-commit.sh`
- **Config**: `.gemini/settings.json`
- **Contexto**: `GEMINI.md`

## 🔊 Notificaciones
- **Éxito**: `victory-sound.sh` se dispara tras el auto-commit exitoso.
- **Acción Requerida**: `permission-sound.sh` para prompts críticos.

---
*Rama: dev-gemini | Versión: 1.0.0 (Agnóstica)*
