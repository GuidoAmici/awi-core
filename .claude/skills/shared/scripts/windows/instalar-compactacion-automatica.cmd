@echo off
rem Registra la tarea programada que compacta WSL sola (doble clic, una sola vez).
rem Pide permisos de administrador esta vez; despues la tarea corre sin preguntar.
rem Para sacarla: compactar-wsl.ps1 -Desinstalar.
powershell -NoProfile -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%~dp0compactar-wsl.ps1\" -Instalar'"
