# Issue #21 — Promo badges por canal (absorbe #22)

- **PR:** https://github.com/GuidoAmici/newhaze-webapp/pull/174 (`feat/21-promo-badges` → `stg`)
- **Issue:** https://github.com/GuidoAmici/newhaze-webapp/issues/21 (comentado con el resumen)
- **Rol:** Frontend Developer (AWI)
- **Repo:** `newhaze-webapp`

## Qué se hizo

Absorbe #21 y #22 en un solo PR (mismos dos archivos, mismo mecanismo — decidido en grilling 2026-08-10):

1. **Eje retailer (#21)** — badges globales G1 (≥$100k, piso duro → desbloquea precio growshop) / G2 (≥$200k, envío bonificado) / G3 (≥$500k, −10%) en `OrderTotalBar`. Gris/no-alcanzado → verde+✓/alcanzado; hover/focus explica cuánto falta. El CTA "Enviar pedido" se habilita recién al cruzar G1. Mensaje del piso duro con fallback a texto plano (`/donde-comprar`, #25, no existe todavía — `TODO(#25)` explícito en el código).
2. **Eje mayorista (#22)** — resalta la fila May.x alcanzada en la escalera de cada card según la cantidad viva del armador. Se extrajo `reachedWholesalerRow(item, qty)` en `pricing.ts`, el mismo helper que ya fijaba el precio unitario (`unitPriceFor`), para que precio y resaltado no puedan divergir. `qty === 0` (y por debajo del primer bulto) nunca cuenta como alcanzado.

## Archivos tocados

- `src/lib/pricing.ts` — nuevo `reachedWholesalerRow`; `unitPriceFor` refactorizado para usarlo.
- `src/lib/reseller-mechanism.ts` — nuevo `retailerTierStatus(total)` sobre `RETAILER_TIERS` (#88).
- `src/components/catalog/order-builder.tsx` — badges G1/G2/G3, piso duro del CTA, `useOrderBuilderQuantities` (lectura tolerante del mismo store, para que `product-card.tsx` pueda leer cantidades sin requerir provider en el path consumer de los tests).
- `src/components/catalog/product-card.tsx` — resaltado de la escalera mayorista.
- Tests nuevos/actualizados: `pricing.test.ts`, `reseller-mechanism.test.ts` (nuevo), `order-builder.test.tsx`, `product-card.test.tsx`.

## Verificado

- `npx vitest run` → 254/254 tests.
- `npm run typecheck` → sin errores.
- `npm run lint` → sin errores (2 warnings preexistentes, no relacionados).
- `npm run build` → build de producción exitoso (con instalación real de dependencias en el worktree — la instancia venía sin `node_modules`).

## Fuera de alcance (según el brief)

- "Enviar pedido" (#24): no implementado; el CTA solo cambia su estado disabled según G1.
- `/donde-comprar` (#25): no implementado; el link cae a texto plano con `TODO(#25)`.
- No se agregaron specs E2E: la única cuenta de prueba de la suite Playwright (`e2e@newhaze.test`) es consumer sin organización — no hay forma 100% read-only de ejercitar retailer/wholesaler sin una cuenta B2B de prueba en stg (decisión de datos fuera de este slice). Queda anotado en el PR como posible follow-up.

## Nota de contexto

El worktree se creó originalmente desde `ci/151-en-prod-label` en vez de `origin/stg` (un commit de más, no relacionado — CI workflow). Se recreó la rama `feat/21-promo-badges` limpia desde `origin/stg` antes de commitear, para no arrastrar ese commit ajeno al PR.

## Actualización post-revisión (commit `6c96f67`)

El primer push (`4fb1849`) rompía `/catalogo` en el preview con **500**: `product-card.tsx` es server component y llamaba `useOrderBuilderQuantities()` (hook de React) directo en su cuerpo. Ningún test unitario lo detectaba (jsdom no distingue server/client, y `/catalogo` es dinámica — el build no la prerrenderiza). Lo atrapó el gate E2E contra el preview real.

**Fix:** extraída la escalera mayorista a `src/components/catalog/wholesaler-ladder.tsx`, un client component chico (`"use client"`) que recibe el ítem por props y ahí sí llama al hook. `product-card.tsx` vuelve a ser 100% server component.

De paso, corregido un bug de copy real detectado en la misma revisión: una fila ya superada de la escalera (ej. May.1 con `qty=10` y May.2 ya alcanzado) mostraba "Faltan 0 unidades para alcanzar May.1." — corregido a "May.1 superado — ahora estás en May.2.", con test de regresión nuevo.

**Verificado con servidor real, no solo tests unitarios:**
- `npm run build && npm start` con `.env.local` real → `curl /catalogo` → 200, `curl /` → 200.
- `npx playwright test` contra ese server real → los 3 specs rotos (`catalogo.spec.ts:7`, `catalogo.spec.ts:47`, `home.spec.ts:24`) pasan.
- Confirmado también contra el preview real de Vercel del commit `6c96f67` (`https://newhaze-webapp-git-feat-21-promo-badges-rabbitek.vercel.app`) → `/catalogo` y `/` responden 200.
- `vitest` 255/255, `tsc --noEmit` limpio, `eslint` limpio.

PR body actualizado con la sección "Sólo vos" corregida (links directos y verificados al preview, en vez de pedir la URL).
