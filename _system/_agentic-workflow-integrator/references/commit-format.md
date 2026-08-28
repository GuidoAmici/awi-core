# Commit Format

AWI usa **Conventional Commits con scope**. (Reemplaza al viejo prefijo `cos:`.)

```
<tipo>(<scope>): <descripción en imperativo>

docs(newhaze): add BDR-0001 pricing de pHmetro
feat(afin): login con Supabase
fix(newhaze): corregir margen de growshop en la lista #27
chore(sync): stage local changes
chore(sync): materializar los repos nuevos del manifiesto
refactor(awi): simplificar el ciclo de contexto
```

## Tipos

| Tipo | Para qué |
|---|---|
| `feat` | nueva capacidad/feature |
| `fix` | corrección de un error |
| `docs` | contenido del vault, wikis, BDR/ADR, notas, daily/weekly |
| `chore` | mantenimiento: sync, bumps, scaffolding, activar/desactivar, mover/renombrar |
| `refactor` | reestructurar sin cambiar comportamiento |
| `perf` · `test` · `build` · `ci` · `style` · `revert` | uso estándar de Conventional Commits |

## Scope

El scope es **opcional pero recomendado**. Suele ser:

- el **slug de la org/cliente** (`newhaze`, `afin`) — mapea a las entradas del manifiesto,
- `awi` para el sistema/vault,
- `sync` para operaciones de sincronización automáticas.

## Filtro de actividad

Los reportes (`/today`, `/history`, `/quarter`) filtran por prefijo de
Conventional Commit. Durante la transición el filtro también matchea el viejo
`cos:` para no perder historial:

```bash
git log -E --grep='^(cos|feat|fix|docs|chore|refactor|perf|test|build|ci|style|revert)(\([^)]+\))?!?: '
```

## Identidad del autor en repos de cliente

En un repo de cliente el commit sale con el `user.email` **local del repo**, no
con el del perfil AWI. Se comprueba antes de commitear:

```bash
git config user.email   # dentro del repo del codebase, no en el vault
```

No es cosmética: Vercel resuelve el autor del commit contra sus colaboradores y
**bloquea el deployment** de un commit cuyo email no reconoce. Le pasó a un
agente delegado el 2026-08-28 en `newhaze-webapp` (issue #193) commiteando con
`newhazetek@gmail.com` en vez de `guido@newhaze.ar`: el primer push quedó sin
preview y hubo que rehacer el commit.
