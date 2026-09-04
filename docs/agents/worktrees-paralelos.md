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

## El mecanismo

Documentar esto no alcanzó: el 2026-09-04, con este doc ya escrito unas horas antes, dos sesiones se pisaron el checkout de `newhaze-webapp` y una entregó un commit colgado de la rama de la otra. Desde entonces hay mecanismo, no sólo modelo mental:

```bash
python3 .claude/skills/shared/scripts/worktree.py provision <codebase> <rama>
python3 .claude/skills/shared/scripts/worktree.py list      # quién tiene qué
python3 .claude/skills/shared/scripts/worktree.py status    # quién tomó cada checkout principal
python3 .claude/skills/shared/scripts/worktree.py release <codebase>
```

`provision` crea el worktree, symlinkea los archivos ignorados que la app necesita (`.env.local` y hermanos), le asigna un puerto libre en `.worktree-port` y avisa si el repo trae stack de base de datos.

`worktree-guard.py` (PreToolUse) bloquea un `git checkout` de rama sobre un checkout principal que otra sesión tiene tomado. El lease vive en `.claude/tmp/checkout-leases.json`, vence a las 8 horas y no se versiona. La regla operativa está en INSTRUCTIONS.md, que se carga en cada sesión.

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

Lo que se hizo a mano ese día es lo que `worktree.py provision` hace ahora en un comando — salvo `playwright.config.ts` leyendo `.worktree-port`, que es config del repo y viaja por merge como cualquier commit.
