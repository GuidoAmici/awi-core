#!/bin/bash
# Puente del MCP doppler: toma el token de la CLI de Doppler cada vez que el MCP
# arranca, en vez de leer DOPPLER_TOKEN de ~/.claude/settings.json. Así el token
# no queda copiado en texto plano, y rotarlo es `doppler login`: basta con que la
# sesión relance el MCP.
#
# doppler va con </dev/null: si no, se come el stdin, que es el canal JSON-RPC
# del MCP.
set -u

token=""
if command -v doppler >/dev/null 2>&1; then
    token="$(doppler configure get token --plain </dev/null 2>/dev/null)"
fi
token="${token:-${DOPPLER_TOKEN:-}}"

if [ -z "$token" ]; then
    echo "doppler MCP: no hay token (corré \`doppler login\`)." >&2
    exit 1
fi

export DOPPLER_TOKEN="$token"
exec npx -y @dopplerhq/mcp-server
