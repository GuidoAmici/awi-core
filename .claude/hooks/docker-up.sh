#!/bin/bash
# Levanta Docker Desktop desde WSL2 y deja la integración WSL prendida.
# Usage: bash .claude/hooks/docker-up.sh [status] [--timeout N] [--no-wsl-fix]
#
# En esta máquina Docker Desktop corre en Windows y WSL2 le habla de dos formas
# muy distintas, que conviene no confundir:
#
#   integración WSL   un cliente docker LINUX dentro de la distro, hablándole al
#                     engine por socket. Es la forma rápida y la que esperan las
#                     herramientas (supabase CLI, testcontainers).
#   interop           el shim /mnt/c/.../resources/bin/docker, un script sh que
#                     cruza a Windows en cada llamada. Funciona, pero es lento y
#                     traduce rutas de forma distinta.
#
# Que `docker` aparezca en el PATH NO significa que la integración esté
# prendida: el shim de interop también aparece. Se distingue por dónde vive el
# binario — bajo /mnt/c es interop.
#
# La integración se prende en settings-store.json, que Docker Desktop lee al
# arrancar. Por eso se edita con Docker CERRADO: hacerlo con Docker corriendo
# lo pisa al salir.
#
# Salidas: 0 = daemon respondiendo. 1 = no arrancó dentro del timeout, o Docker
# Desktop no está instalado donde se lo espera.

set -uo pipefail

TIMEOUT=180
MODO="up"
ARREGLAR_WSL=1
while [[ $# -gt 0 ]]; do
  case "$1" in
    status) MODO="status"; shift ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    --no-wsl-fix) ARREGLAR_WSL=0; shift ;;
    *) shift ;;
  esac
done

SHIM="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
DESKTOP_EXE="C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe"
SETTINGS="/mnt/c/Users/$(powershell.exe -NoProfile -Command '$env:USERNAME' 2>/dev/null | tr -d '\r\n')/AppData/Roaming/Docker/settings-store.json"
DISTRO="${WSL_DISTRO_NAME:-Ubuntu}"

cliente_docker() {
  local encontrado
  encontrado="$(command -v docker 2>/dev/null)"
  if [[ -n "$encontrado" ]]; then echo "$encontrado"; return; fi
  [[ -x "$SHIM" ]] && echo "$SHIM"
}

DOCKER="$(cliente_docker)"
if [[ -z "$DOCKER" ]]; then
  echo "No encuentro el cliente de docker (ni en PATH ni en $SHIM)." >&2
  exit 1
fi

daemon_ok() { "$DOCKER" ps -q &>/dev/null; }

# Integración prendida = hay un cliente docker que NO vive bajo /mnt/c.
integracion_ok() {
  local encontrado
  encontrado="$(command -v docker 2>/dev/null)" || return 1
  [[ -n "$encontrado" && "$encontrado" != /mnt/c/* ]]
}

estado_integracion() {
  integracion_ok && echo "prendida" || echo "apagada (usando el shim de interop)"
}

# Sólo con Docker cerrado: escribe la distro actual en la lista de integradas.
prender_integracion() {
  [[ -f "$SETTINGS" ]] || { echo "  No encuentro settings-store.json; dejo la integración como está." >&2; return 1; }
  python3 - "$SETTINGS" "$DISTRO" <<'PY'
import json, sys
ruta, distro = sys.argv[1], sys.argv[2]
with open(ruta, encoding="utf-8-sig") as fh:
    cfg = json.load(fh)
distros = cfg.get("IntegratedWslDistros") or []
if not isinstance(distros, list):
    distros = []
if distro not in distros:
    distros.append(distro)
cfg["IntegratedWslDistros"] = distros
cfg["EnableIntegrationWithDefaultWslDistro"] = True
with open(ruta, "w", encoding="utf-8") as fh:
    json.dump(cfg, fh, indent=2)
print(f"  Integración WSL habilitada para «{distro}» en settings-store.json.")
PY
}

if [[ "$MODO" == "status" ]]; then
  daemon_ok && echo "Docker corriendo. Integración WSL: $(estado_integracion)." && exit 0
  echo "Docker está caído. Integración WSL: $(estado_integracion)."
  exit 1
fi

if daemon_ok; then
  echo "Docker ya está corriendo. Integración WSL: $(estado_integracion)."
  # No se reinicia Docker por su cuenta para arreglar la integración: hay
  # contenedores vivos y bajarlos sorprendería a quien los esté usando.
  integracion_ok || echo "  Para prenderla hace falta reiniciar Docker: cerralo y volvé a correr este script."
  exit 0
fi

command -v powershell.exe &>/dev/null || {
  echo "Docker está caído y no hay powershell.exe para levantarlo desde WSL." >&2
  exit 1
}

echo "Docker está caído. Levantando Docker Desktop…"
if (( ARREGLAR_WSL )) && ! integracion_ok; then
  prender_integracion || true
fi

powershell.exe -NoProfile -Command "Start-Process -FilePath '$DESKTOP_EXE'" >/dev/null 2>&1

# Docker Desktop abre la app mucho antes de que el engine acepte conexiones:
# se espera al daemon, no al proceso.
INICIO=$SECONDS
while (( SECONDS - INICIO < TIMEOUT )); do
  if daemon_ok; then
    echo "Docker respondiendo tras $(( SECONDS - INICIO )) s. Integración WSL: $(estado_integracion)."
    exit 0
  fi
  sleep 5
done

echo "Docker no respondió en ${TIMEOUT} s. Puede necesitar atención manual (login, actualización pendiente)." >&2
exit 1
