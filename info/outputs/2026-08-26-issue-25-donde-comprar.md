# Issue #25 — `/donde-comprar`, directorio público de growshops

**Repo:** `newhaze-webapp` · **Rama:** `feat/25-donde-comprar` · **PR:** [#175](https://github.com/GuidoAmici/newhaze-webapp/pull/175) contra `stg` (CI en verde, sin mergear) · **Issue:** [#25](https://github.com/GuidoAmici/newhaze-webapp/issues/25)

## Qué se hizo

Página pública `/donde-comprar` que lista organizaciones `type='retailer'` + `is_public=true` (taxonomía correcta según ADR-0005 §6b — el título del issue quedó de un diseño viejo que decía `type='Growshop'`, ese type ya no existe en el CHECK de la tabla). Complementa a `/revendedores` (#88): esa es para que el growshop se asocie, esta es para que el consumidor lo encuentre. Reusa su vocabulario visual (tipografía, tokens `nh-*`, eyebrow + H1 uppercase con resaltado accent).

**El estado vacío es de primera clase**, no un `<p>` de relleno: hoy las 48 orgs retailer del histórico tienen `is_public=false` (opt-in pendiente, explícitamente fuera de alcance), así que la página nace vacía. Verificado contra el preview real del commit final (`https://newhaze-webapp-6h81uc9sh-rabbitek.vercel.app/donde-comprar`, `curl` → 200): muestra el estado vacío correcto (copy + link a `/catalogo` + link a `/revendedores`).

## Hallazgo de seguridad, en dos vueltas (no cubierto por el brief)

**Primera vuelta:** la RLS de `organizations` (policy `organizations_directory_read`, issue #9) acotaba **filas** para `anon` (`is_public AND status='approved'`) pero no **columnas**: por los default privileges heredados del baseline legacy, `anon` tenía `SELECT` de tabla completa y podía leer `cuit`, `balance_ars`, `status`, `type`, `approved_by/at`. Verificado en stg vía `information_schema.column_privileges`.

**Segunda vuelta (encontrada en revisión sobre mi propio arreglo):** la primera versión de la vista `organizations_directory` tenía `GRANT SELECT` pero ningún `REVOKE` propio. Como Postgres le da `arwdDxtm` (ALL) a toda relación nueva —tabla o vista— para `anon`/`authenticated` (`pg_default_acl`), y la vista corre sin `security_invoker` (con los privilegios del dueño, exenta de la RLS de `organizations`), un `anon` podía `UPDATE`/`DELETE` por la vista y esa escritura llegaba a la tabla real saltándose la RLS por completo. De lectura a escritura, mismo perfil de riesgo.

**Arreglo final, dos capas**, aplicado y verificado en stg de verdad (el job `migrate-stg` corre en el PR, antes del merge):
- `REVOKE ALL ON public.organizations_directory FROM anon, authenticated` antes del `GRANT SELECT`.
- La vista pasa a `SELECT DISTINCT` — no cambia el resultado (`id` es PK de `organizations`) pero la descalifica de ser automáticamente actualizable: INSERT/UPDATE/DELETE fallan siempre con SQLSTATE `55000` ("Views containing DISTINCT are not automatically updatable"), incluso si algún `REVOKE` futuro se pierde. Confirmado ejecutando de verdad como `anon` contra stg, antes y después de aplicar: `has_table_privilege` → solo `SELECT`; `information_schema.views.is_updatable/is_insertable_into` → `NO`.

**Nota sobre el contrato expand-only:** el `REVOKE` sobre `organizations` es, en la letra, una contracción (rompe "solo aditivo"). Es seguro en este caso puntual porque se verificó que ninguna ruta desplegada dependía del grant de `anon` sobre esa tabla — las tres únicas consultas del código (`/cuenta/organizaciones/[orgId]`, su `/editar`, `/panel/organizaciones`) están detrás de `requireUser`/rutas internas y usan el cliente de sesión (`authenticated`), nunca el cliente público. Documentado explícitamente en el PR para que un revisor no tenga que deducirlo.

Esto obligó a tocar un test preexistente, `supabase/tests/identity_rls_test.sql` (su aserción de `anon` asumía `SELECT` directo sobre la tabla base, ahora `42501`), y a sincronizar `database.types.ts`: además de las columnas de la vista, el generador emite 5 entradas nuevas de `Relationships` (una por cada FK hacia `organizations` en `invoices`, `org_x_users`, `profiles`, `receipts`, `sales_orders`, porque la vista expone `id`). Esos 5 hunks se tomaron **verbatim del diff del log de CI** (`gh run view --log-failed`), no se dedujeron a mano — el contrato database-first (ADR-0001) exige que los tipos commiteados sean la salida real del generador.

## Verificado — CI en verde

Run [`32943692680`](https://github.com/GuidoAmici/newhaze-webapp/actions/runs/32943692680), commit `6c37240` (HEAD del PR): `Lint + tipos + tests + build`, `pgTAP — RLS y RPCs (stack local)` (incluye el gate de tipos), `Migraciones → New Haze DB stg`, `Deploy preview (PR) → Vercel` y `Playwright` — todos `success`.

Local: `npm run typecheck` 0 errores, `npm run lint` 0 errores (2 warnings preexistentes no relacionados), `npm test` 241/241 (37 archivos), `npm run build` OK.

E2E (`tests/donde-comprar.spec.ts`) confirmado 100% read-only por inspección (sin ningún método de escritura) — corrido y en verde en CI.

## Fuera de alcance, marcado explícitamente en el PR y en el issue

1. **Link desde el mensaje del piso G1 (#21)** — ese issue sigue abierto (PR #174, toca `src/components/catalog/`, de otro agente en paralelo). La ruta ya existe, lista para ese link cuando mergee.
2. **Agrupar por ciudad/provincia** — `organizations` no tiene columna estructurada de ubicación, solo `address` como texto libre. Se implementó una grilla simple sin agrupar; agrupación real necesitaría una columna nueva (cambio de esquema aparte, no pedido por este issue).
3. **Opt-in de las 48 orgs legacy** — fuera de alcance como estaba definido en el brief.

## Lecciones del proceso (para dejar constancia)

- Un `GRANT` no revoca privilegios preexistentes — en Postgres/Supabase, toda relación nueva (tabla o vista) nace con `ALL` para `anon`/`authenticated` vía `pg_default_acl`; hay que revocar explícitamente antes de otorgar el mínimo necesario, incluso sobre objetos "de solo lectura" por diseño.
- Sin Docker local, el gate de CI (`pgtap`, incluido el diff de tipos generados) es el único oráculo real para cambios de esquema — no alcanza con razonar sobre lo que el generador "debería" emitir; hay que leer su salida real (tomada del log de CI cuando no se puede correr localmente) y aplicarla verbatim.

## Estado

PR abierto, CI en verde, no mergeado por mí (instrucción explícita de no mergear el propio PR). Comentarios de avance y cierre publicados en el issue #25. La sección "Sólo vos" del PR queda para revisión humana de copy y diseño del estado vacío, con el link directo al preview verificado.
