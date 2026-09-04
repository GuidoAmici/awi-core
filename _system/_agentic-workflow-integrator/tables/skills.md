---
type: reference
title: AWI Skills
---

# AWI Skills

Cuando el operador tipea `/<comando>`, leé y ejecutá `.claude/skills/<comando>/SKILL.md`.
Si el archivo no existe, decile que el comando no está disponible.

`.claude/skills/shared/` no es una skill: es la carpeta de scripts que las demás importan.

## El día

| Comando | Qué hace |
|---|---|
| `/today` | Hub diario — abrir el día, ver o refrescar el plan, cerrarlo. Se puede correr varias veces |
| `/today-start` | Atajo a `/today` → «Start my day» |
| `/today-end` | Atajo a `/today` → «End my day» |
| `/break <motivo>` | Registra un descanso en el daily; `/break back` marca la vuelta |
| `/week` | El plan de la semana: tareas elegidas, modelo mental, avance |
| `/week-review` | Ritual del viernes — repriorizar lo pendiente y elegir el lote de la semana que viene |
| `/quarter` | Plan trimestral con objetivos, hitos de proyecto y hoja de ruta |
| `/year` | Plan anual con objetivos estratégicos y metas por trimestre |
| `/new <texto>` | Captura rápida — clasifica y archiva en el filetree |
| `/history` | Actividad reciente de git, legible |
| `/wrap-session` | Ritual de cierre — hilos abiertos, observaciones, publicación del contexto |

## Issues y planificación

| Comando | Qué hace |
|---|---|
| `/triage` | Triar issues por la máquina de estados de roles de triage |
| `/to-prd` | Convertir el contexto de la conversación en un PRD y publicarlo al tracker |
| `/to-issues` | Partir un plan o PRD en issues agarrables por separado, en rebanadas verticales |
| `/grill-with-docs` | Sesión de grilling contra el modelo de dominio; actualiza `CONTEXT.md` y ADRs sobre la marcha |
| `/delegate-issue` | Despachar issues `ready-for-agent` a agentes en background |

## Código

| Comando | Qué hace |
|---|---|
| `/improve-codebase-architecture` | Buscar oportunidades de profundizar módulos, guiado por `CONTEXT.md` y los ADRs |
| `/write-a-skill` | Crear una skill nueva con estructura y divulgación progresiva |
| `/zoom-out` | Pedir contexto más amplio o una perspectiva de más alto nivel |

## Instancia, usuarios y organizaciones

| Comando | Qué hace |
|---|---|
| `/awi-introduction` | Onboarding de primera vez — GitHub, idioma, preferencias, scaffold, y termina en `/today` |
| `/awi-initialize` | Clonar todo lo activo en `user-submodules.json`, más los codebases activos de cada org |
| `/awi-user` | Gestión unificada — ver, cambiar, crear usuarios; materializa `my-awi-user` |
| `/awi-user-create <usuario>` | Crear un usuario nuevo y su perfil de persona |
| `/awi-user-login <usuario>` | Cargar el perfil de una persona para esta sesión |
| `/awi-org <nombre>` | Agregar una organización — desde cero o importando un repo existente |
| `/awi-submodule-toggle <nombre>` | Prender o apagar cualquier repo de AWI: orgs, system repos, o un codebase suelto |
| `/awi-update` | Traer la última versión del harness publicada en `main` |

## Índices de contexto

| Comando | Qué hace |
|---|---|
| `/check-index` | Auditar qué carpetas no tienen `.abstract.md` / `.overview.md`, sin modificar nada |
| `/reindex` | Crear o actualizar esos archivos siguiendo la convención OpenViking L0/L1 |
| `/awi-layer-index` | Auditar y arreglar L0/L1 en `_system/`, `_data/users/` y `_data/organizations/` |
