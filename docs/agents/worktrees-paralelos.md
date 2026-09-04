---
tipo: agentes
capa: operacion
descripcion: Aislar agentes que trabajan en ramas distintas del mismo repo con git worktree.
last-updated: 2026-09-04
artifacts:
  - url: https://claude.ai/code/artifact/e07b050f-78c1-4cd9-9efe-964e66e73485
    entrega: Modelo mental de git worktree para agentes en paralelo, y los cuatro recursos compartidos que sobreviven al aislamiento
    estado: pendiente
    fecha: 2026-09-04
---

# Worktrees: varios agentes, un repo

Varios agentes en el mismo directorio de trabajo **no funciona**: un working tree tiene un solo `HEAD`, así que el `git checkout` de uno reescribe los archivos que el otro está leyendo. La solución es `git worktree` — un directorio por rama, un solo `.git`.

Los worktrees de Claude Code viven en `.claude/worktrees/`. `EnterWorktree` crea uno y muda la sesión; `isolation: "worktree"` le da el suyo a cada subagente.

## Lo que el worktree NO aísla

El aislamiento es del checkout, no de la máquina. Estos cuatro recursos siguen compartidos y son el origen de casi todos los errores:

| Recurso | Síntoma | Arreglo |
|---|---|---|
| Archivos en `.gitignore` | La app no arranca en el worktree nuevo | Symlink de `.env.local`; `npm install` propio |
| Puerto del dev server | `reuseExistingServer` hace que un agente testee la app de otro | Puerto por worktree en `.worktree-port` |
| Stack local de base de datos | Migraciones que se pisan | Serializar, o branches remotas |
| Config versionada | Un fix en una rama no llega a las otras | Se propaga por merge, como cualquier commit |

De los cuatro, el del puerto es el único que **no falla**: reporta resultados sobre el código equivocado. Ver el artifact para el mecanismo completo.

## Containers

Un container aísla el sistema operativo, no git: dos containers montando el mismo directorio comparten un working tree y se pisan igual. La combinación que funciona es **un worktree por rama, un container montando ese worktree** — y sólo se paga cuando hacen falta stacks de base de datos paralelos.

## Estado en newhaze-webapp

Provisionado el 2026-09-04: `.env.local` symlinkeado y `node_modules` instalado en los tres worktrees, `.worktree-port` en 3000/3001/3002, y `playwright.config.ts` leyendo ese archivo. El cambio de config vive por ahora sólo en la rama `stg`.
