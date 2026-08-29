#!/usr/bin/env bash
#
# SessionStart — inyecta INSTRUCTIONS.md entero al abrir la sesión.
#
# Existe porque las reglas de escritura —el orden de la respuesta, el TLDR, la
# paráfrasis de identificadores, los bloques pegables— rigen desde el primer turno,
# y CLAUDE.md sólo mandaba leer el archivo «antes de cualquier operación del vault».
# Una sesión que nunca toca el vault nunca las cargaba, que es justo donde más se
# notaba la falta: respuestas sin estructura, identificadores desnudos y comandos
# que el operador no podía pegar.
#
# El archivo entero, no un tramo: la extracción por secciones se desincroniza en
# silencio y el modo de falla es no darse cuenta.
#
# Si el archivo no está —instancia a medio scaffoldear, worktree parcial— el hook
# sale en silencio. Romper el arranque de la sesión es peor que no cargar las reglas.

set -euo pipefail

INSTRUCTIONS="${CLAUDE_PROJECT_DIR:-.}/_system/_agentic-workflow-integrator/INSTRUCTIONS.md"

[ -r "$INSTRUCTIONS" ] || exit 0

printf '%s\n\n' "Reglas del vault — INSTRUCTIONS.md, fuente de verdad, cargado al abrir la sesión. Rige desde este turno, sin necesidad de volver a leerlo:"
cat "$INSTRUCTIONS"
