#!/bin/bash
# Puente del MCP supabase-newhaze: lee el token de Windows cada vez que el MCP
# arranca, en vez de heredarlo del entorno de la sesión. El entorno de la sesión
# sale de ~/.profile al hacer login, y si en ese momento powershell.exe no
# respondía (o el login no lo corrió), el MCP arrancaba sin token y Supabase
# contestaba «Unauthorized». Con esto, rotar el token en Windows alcanza: basta
# con que la sesión de Claude relance el MCP.
#
# Del registro (PowerShell, scope User) por la misma razón que ~/.profile:
# cmd.exe hereda el entorno del proceso de Windows que lanzó WSL y puede ver el
# valor viejo. Si Windows no responde, cae al entorno.
#
# Va por SUPABASE_ACCESS_TOKEN y no por --access-token: un argumento se ve en `ps`.
# powershell.exe va con </dev/null: si no, se come el stdin, que es el canal
# JSON-RPC del MCP, y el servidor arranca sin recibir ningún pedido.
set -u

VAR=NewHaze_Supabase_Challenger_full_access
token=""
if command -v powershell.exe >/dev/null 2>&1; then
    token="$(cd /mnt/c 2>/dev/null && powershell.exe -NoProfile -NonInteractive -Command "[Environment]::GetEnvironmentVariable('$VAR','User')" </dev/null 2>/dev/null | tr -d '\r\n')"
fi
case "$token" in
    '' | %*%) token="${!VAR:-}" ;;
esac

if [ -z "$token" ]; then
    echo "supabase-newhaze MCP: no encontré $VAR (ni en las variables de usuario de Windows ni en el entorno)." >&2
    exit 1
fi

export SUPABASE_ACCESS_TOKEN="$token"
exec npx -y @supabase/mcp-server-supabase@latest
