#!/bin/bash
# Levanta Docker Desktop desde WSL2 cuando el daemon está caído.
# Usage: bash .claude/hooks/docker-up.sh [status] [--timeout N]
#
# En esta máquina Docker Desktop corre en Windows y WSL2 le habla por un named
# pipe. Cuando Docker Desktop está cerrado —después de un `wsl --shutdown`, o
# de reiniciar— todo lo que dependa de contenedores falla con "failed to
# connect to the docker API", y hasta ahora había que abrirlo a mano.
#
# El agente no tiene que pedirle eso al operador: puede lanzarlo él.
#
# Salidas: 0 = daemon respondiendo (ya lo estaba, o arrancó). 1 = no arrancó
# dentro del timeout, o Docker Desktop no está instalado donde se lo espera.

set -uo pipefail

TIMEOUT=180
MODO="up"
while [[ $# -gt 0 ]]; do
  case "$1" in
    status) MODO="status"; shift ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

DOCKER_EXE="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
DESKTOP_EXE="C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe"

# `docker` nativo si la integración WSL está activa; si no, el .exe del host.
if command -v docker &>/dev/null; then
  DOCKER=(docker)
elif [[ -x "$DOCKER_EXE" ]]; then
  DOCKER=("$DOCKER_EXE")
else
  echo "No encuentro el cliente de docker (ni en PATH ni en $DOCKER_EXE)." >&2
  exit 1
fi

daemon_ok() { "${DOCKER[@]}" ps -q &>/dev/null; }

if daemon_ok; then
  echo "Docker ya está corriendo."
  exit 0
fi

if [[ "$MODO" == "status" ]]; then
  echo "Docker está caído."
  exit 1
fi

if ! command -v powershell.exe &>/dev/null; then
  echo "Docker está caído y no hay powershell.exe para levantarlo desde WSL." >&2
  exit 1
fi

echo "Docker está caído. Levantando Docker Desktop…"
# -NoProfile para no arrastrar el perfil del usuario; Start-Process no bloquea,
# así que el arranque real se espera con el polling de abajo.
powershell.exe -NoProfile -Command "Start-Process -FilePath '$DESKTOP_EXE'" >/dev/null 2>&1

# Docker Desktop tarda bastante en aceptar conexiones: primero levanta la app,
# después la VM del engine. Se espera al daemon, no al proceso.
ESPERADO=$SECONDS
while (( SECONDS - ESPERADO < TIMEOUT )); do
  if daemon_ok; then
    echo "Docker respondiendo tras $(( SECONDS - ESPERADO )) s."
    exit 0
  fi
  sleep 5
done

echo "Docker no respondió en ${TIMEOUT} s. Puede necesitar atención manual (login, actualización pendiente)." >&2
exit 1
