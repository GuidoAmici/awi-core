---
tipo: agentes
capa: operacion
descripcion: Aislar agentes que trabajan en ramas distintas del mismo repo con git worktree.
last-updated: 2026-09-04
artifacts:
  - url: null
    entrega: Modelo mental de git worktree para agentes en paralelo, y los recursos compartidos que sobreviven al aislamiento
    estado: fuente-solo
    nota: publicado desde otra cuenta; la URL dejó de resolver. El fuente vive en docs/agents/artifacts/worktrees.html
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

Cerrado el 2026-09-04:

- **Puerto por worktree** — [#239](https://github.com/GuidoAmici/newhaze-webapp/pull/239) en `stg`, propagado por cherry-pick a las ramas activas. Los cuatro worktrees resolvieron `:3000`–`:3003` verificado.
- **Guard del stack local** — [#241](https://github.com/GuidoAmici/newhaze-webapp/pull/241) en `stg`. `scripts/supabase-guard.mjs`, enganchado en `db:types`, `db:types:check` y `test:e2e:local`.
- **Provisión manual** — `.env.local` symlinkeado y `node_modules` instalado en cada worktree.

El merge completo de `stg` hacia las ramas de feature chocaba con trabajo en vuelo de esos agentes, así que viajó sólo el commit del puerto. Es el patrón a repetir: propagar el fix, no la base entera.

## Una instancia de base de datos por rama

El guard detecta la colisión pero no la evita. Aislar de verdad pide un stack por worktree, y eso **sí es posible**: el CLI soporta instancias paralelas con distinto `project_id` y puertos, seleccionables con `supabase start --workdir`. La prueba local es que ya conviven los stacks de `newhaze-webapp` y `afin-website`.

El límite es la RAM. Medido en esta máquina: **~1,7 GiB y 11 contenedores por stack**. El host tiene 32 GB pero `.wslconfig` capa WSL2 en 10 GB, así que hoy entran uno o dos. Subir ese tope es el desbloqueo más barato.

Para que las instancias no se acumulen, Claude Code expone hooks **`WorktreeCreate` / `WorktreeRemove`** en `.claude/settings.json`: el primero provisiona (env, deps, puertos determinísticos), el segundo limpia al cerrar el worktree. `WorktreeRemove` es fire-and-forget — no puede bloquear el cierre. Atención al [issue #37611](https://github.com/anthropics/claude-code/issues/37611): definir `WorktreeCreate` desactiva el prompt de limpieza al salir de la sesión.

### Que no se acumulen

El riesgo de un stack por worktree es el bloat: sesiones que mueren sin bajar el suyo van comiendo RAM hasta que no se puede levantar nada, y alguien tiene que ir a mirar contenedores a mano.

`.claude/hooks/supabase-sweep.py` corre en `SessionStart` y reconcilia. **Barrido al arranque, no limpieza al cierre**: una sesión que se muere no ejecuta su propio cleanup, así que la limpieza no puede depender de que el cierre sea limpio — y los cierres sucios son justamente los que dejan basura.

Dos criterios, conservadores a propósito (parar un stack en uso es peor que dejar uno de más):

| Criterio | Qué mira | Acción |
|---|---|---|
| huérfano | el `project_id` no corresponde a ningún `supabase/config.toml` montado en AWI | se baja |
| inactivo | el proyecto existe, ningún checkout suyo tiene lease vigente, y lleva +8 h arriba | se baja |

Todo lo demás se deja en paz. Sin Docker corriendo el hook no hace nada y sale con 0: un barrido que rompe el arranque de la sesión es peor que un stack colgado.

**El Playwright MCP de Docker no resuelve esto.** Es browser automation para que un agente maneje un navegador paso a paso; no aísla bases de datos ni corre la suite del repo. Son problemas distintos.
