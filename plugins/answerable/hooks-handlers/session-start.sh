#!/usr/bin/env bash
#
# SessionStart — inyecta las reglas de `answerable` al abrir la sesión.
#
# Existe porque estas reglas gobiernan la forma de la primera respuesta, no de la
# décima: cargarlas cuando el agente decide leerlas es cargarlas tarde.
#
# El archivo entero, no un tramo. La extracción por secciones se desincroniza en
# silencio y el modo de falla es no darse cuenta.
#
# Si el archivo no está, el hook sale en silencio: romper el arranque de la sesión
# es peor que no cargar las reglas.

set -euo pipefail

REGLAS="${CLAUDE_PLUGIN_ROOT:-.}/rules/answerable.md"

[ -r "$REGLAS" ] || exit 0

cat "$REGLAS"
