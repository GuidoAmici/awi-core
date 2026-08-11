# Issue #66 — Bootstrap de Playwright + gate E2E en Stg CI

**Date:** 2026-08-11
**Agent:** DevOps Automator
**Repo:** newhaze-webapp
**Branch:** `test/66-e2e-playwright` → `stg`
**PR:** https://github.com/GuidoAmici/newhaze-webapp/pull/150
**Issue comment:** https://github.com/GuidoAmici/newhaze-webapp/issues/66#issuecomment-5250862707

## Contexto de arranque

El worktree aislado de este task no traía `_data/organizations/newhaze/codebase/newhaze-webapp` materializado (los codebases de AWI son clones separados fuera del árbol git de `my-awi-instance`, y un `git worktree` fresco no los replica). El sandbox además bloquea cualquier comando `git` de este agente que apunte al checkout compartido. Solución: clon fresco de `https://github.com/GuidoAmici/newhaze-webapp.git` en el scratchpad de la sesión, partiendo de `stg` actualizado (confirmé los 4 merges recientes — #131/#132/#134/#145 — presentes en el HEAD clonado). Todo el trabajo de git (branch, commits, push, PR) se hizo desde ese clon.

Prerrequisito humano verificado con `gh secret list --repo GuidoAmici/newhaze-webapp`: `E2E_TEST_EMAIL` y `E2E_TEST_PASSWORD` ya estaban cargados (junto con `NEWHAZE_SUPABASE_ACCESS_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`, `VERCEL_TOKEN`) — no fue necesario frenar.

## Qué se implementó

- **`playwright.config.ts`** — calcado del de afin-webapp (dev-ci): `baseURL` desde `PLAYWRIGHT_BASE_URL` con fallback a `localhost:3000` + `webServer` (`npm run dev`), chromium only, screenshot/trace on failure, reporter html+list, specs en `tests/`.
- **`tests/helpers.ts`** — `loginViaAuthModal` (signInWithPassword, nunca OAuth) y `dismissSegmentQuizIfPresent` (saltea el overlay de #131 si el usuario de prueba lo dispara).
- **Suite v1 (5 specs, 100% read-only)**: `home.spec.ts`, `catalogo.spec.ts`, `auth.spec.ts`, `learn.spec.ts`, `theme.spec.ts` — mapeados 1:1 contra el brief del issue.
- **`.github/workflows/stg-ci.yml`**:
  - `deploy-preview` (nuevo, solo `pull_request`): deploya tras `migrate-stg`, espera READY (timeout 5 min, portado de afin), expone la URL como output.
  - `deploy-stg`: ahora también expone su URL como output (antes esperaba READY implícitamente pero no la publicaba).
  - `e2e` (nuevo): corre Playwright contra `needs.deploy-preview.outputs.url || needs.deploy-stg.outputs.url` — gate en PR, detección en push. `release-please` sigue dependiendo solo de `deploy-stg` (ADR-0007, sin tocar).
  - Guard `HAS_VERCEL` en los tres jobs nuevos, mismo patrón que `deploy-stg`/`release-please` existentes.
  - No se tocó `migrate-stg` (hay un PR abierto, #148, que lo modifica para otra cosa — no relacionado, no mergeado).
- `package.json`: `@playwright/test` + scripts `test:e2e` / `test:e2e:report`.
- `.gitignore`: `test-results/`, `playwright-report/`, `blob-report/`, `playwright/.cache/`.

## Validación local

Contra datos reales de stg (`.env.local` con la publishable key pública, sin `PLAYWRIGHT_BASE_URL` → Playwright levantó `npm run dev` solo):

- `home`, `catalogo` (7/8 checks; 1 skip limpio — ningún producto con promo activa en este momento), `theme`: **pasan**.
- `learn`: **pasa en local** (el flag `learn` siempre está ON en dev — ver bloqueador abajo para preview/stg).
- `auth`: no pude correrlo completo (no tengo la password del secret). Validé la cadena de selectores (`#auth-email`, `#auth-password`, botón "Entrar") con una password deliberadamente incorrecta contra `e2e@newhaze.test` — respondió "Email o contraseña incorrectos", confirmando que el usuario existe y el flujo llega sin romperse hasta el intento de login.
- `npm run lint`, `npm run typecheck`, `npm test` (vitest, 204 tests): sin regresiones.

## Bloqueador reportado (acción humana pendiente)

`/learn` está detrás del kill switch `learn` (Edge Config, `src/flags.ts`): en local siempre ON, en preview/stg cae a `false` por defecto. Confirmé con `curl` directo al último deploy de `stg` (vía `mcp__vercel__list_deployments`) que `/learn` devuelve **404** hoy. El spec `tests/learn.spec.ts` está bien escrito contra la UI actual pero no va a pasar en CI hasta que alguien prenda la key `learn` en el Edge Config del proyecto `newhaze-webapp` desde el dashboard de Vercel — store compartido entre preview y stg, un solo cambio lo resuelve para ambos entornos. Reportado en el PR y en el comentario del issue; no intenté ningún workaround (requeriría `FLAGS_SECRET`, que no está expuesto como secret de GitHub Actions y con razón).

Nota aparte: verifiqué con `mcp__vercel__get_project_deployment_protection` que Deployment Protection está OFF en el proyecto — el edge case de 401 / header `x-vercel-protection-bypass` del brief no aplica hoy, así que no implementé ese código.

## Archivos relevantes

- `tests/home.spec.ts`, `tests/catalogo.spec.ts`, `tests/auth.spec.ts`, `tests/learn.spec.ts`, `tests/theme.spec.ts`, `tests/helpers.ts`
- `playwright.config.ts`
- `.github/workflows/stg-ci.yml`
