# Issue #193 — cerrar el INSERT directo del cliente sobre pedidos

**Fecha:** 2026-08-28 · **Agente:** `senior-secops` · **Repo:** `GuidoAmici/newhaze-webapp`
**Entregable:** [PR #197](https://github.com/GuidoAmici/newhaze-webapp/pull/197) contra `stg` — **abierto, sin mergear**
**Rama:** `security/193-insert-directo-pedidos`, creada desde `origin/stg` (`85b1fec`), verificado antes de commitear.

---

## Lo primero: no había nada explotable hoy

Auditoría ejecutada, no razonada: stack local con las 26 migraciones aplicadas (`supabase db start`), consultas como `authenticated` y como `anon` con `request.jwt.claims` reales.

| operación | antes del PR | después |
|---|---|---|
| `INSERT` en `sales_orders` (cliente) | pasaba | `42501` |
| `INSERT` en `sales_order_items` (cliente) | pasaba | `42501` |
| `UPDATE`/`DELETE` propios (cliente) | 0 filas — la RLS ya lo negaba | 0 filas |
| `INSERT` con `user_id` de otro | `42501` | `42501` |
| `anon` `INSERT` / `SELECT` | `42501` / 0 filas | `42501` / `42501` |

**Sin fuga de datos ni escalada de privilegios abierta.** Lo único vivo era inserción de basura en el ERP: pedidos con `client_name`/`note`/`date`/`cancelled` arbitrarios y **`id` elegido a mano** (el `WITH CHECK` no lo acotaba), lo que envenena el espacio de PK — la secuencia no se entera y el día que `nextval` llegue ahí, el INSERT del ERP revienta con clave duplicada. Molesto, no crítico. Se vuelve crítico con #24.

### Hallazgo que no estaba en el issue: `TRUNCATE` no pasa por la RLS

`GRANT ALL` del baseline legacy incluye `TRUNCATE`, y `TRUNCATE` **no** es filtrado por Row Level Security. Verificado ejecutándolo: un `authenticated` cualquiera vaciaba `sales_orders` + `sales_order_items` y, por `CASCADE`, también `delivery_notes_issued`. **No alcanzable por la Data API** (PostgREST no emite `TRUNCATE`) — por eso no entra como "explotable hoy" — pero contradice la premisa escrita en `rls_phase1.sql` ("RLS es la única frontera efectiva") y es el mismo gap de #175.

**Es sistémico:** 41 tablas de `public` con `TRUNCATE` para `authenticated`, 40 para `anon`, más `pg_default_acl` dando `arwdDxtm` a toda relación nueva. Este PR arregla 2. **Lo demás necesita issue propio** (ver "ojo humano").

---

## Qué se hizo

`supabase/migrations/20260828120000_pedidos_sin_insert_directo.sql`:

1. `DROP` de `sales_orders_customer_insert` y `sales_order_items_customer_insert`.
2. **Seis políticas `RESTRICTIVE`** (INSERT/UPDATE/DELETE × 2 tablas) que exigen `private.is_internal()`.
3. `REVOKE ALL` de las dos tablas y sus dos secuencias para `anon`.
4. `REVOKE TRUNCATE, REFERENCES, TRIGGER` para `authenticated`.
5. `COMMENT ON TABLE` en ambas, apuntando al contrato.

`supabase/tests/sales_orders_write_surface_test.sql` — 19 aserciones pgTAP.

### La corrección a la propuesta del issue

El issue proponía `REVOKE INSERT ON … FROM authenticated`. **No se puede aplicar.** Los empleados internos se conectan con el **mismo rol Postgres `authenticated`** que los clientes — la RLS los distingue con `private.is_internal()`, los grants no pueden. Ese `REVOKE` dejaría `sales_orders_internal_all` sin efecto para INSERT/UPDATE/DELETE, que es exactamente lo que el issue pide conservar para E4 #28.

La segunda capa se logra igual con las políticas `RESTRICTIVE`: las permissive se combinan con `OR` (una `…_customer_insert` que vuelva reabre el agujero), las restrictive con `AND` (ninguna permissive futura puede habilitar una escritura no interna). Van por comando y no `FOR ALL` porque una restrictive `FOR ALL` aplicaría su `USING` también al `SELECT` y mataría `sales_orders_own_read`.

**No bloquean a #24:** la RLS no aplica al owner de la tabla (no hay `FORCE ROW LEVEL SECURITY`) y la RPC `SECURITY DEFINER` corre como owner.

### Los otros tres puntos del issue

- **DROP vs ALTER vs trigger** → DROP. El piso G1 es una regla sobre el **total**, y las líneas se insertan después de la cabecera: ningún `WITH CHECK` ni trigger por fila ve el pedido completo. Un `CONSTRAINT TRIGGER DEFERRABLE` sí lo vería al COMMIT, pero tendría que reimplementar la regla de precios en SQL y correría también para la RPC → dos copias del mismo cálculo. Una sola puerta.
- **Expand-only (ADR-0017)** → contracción justificada con la misma evidencia y formato que #175: `grep -rn "sales_order" src/` da un comentario y el archivo generado, nada más; el botón de envío está `disabled` por diseño; `anon` no tenía política de lectura, su grant era herencia muerta.
- **Superficie completa** → `UPDATE`/`DELETE` del cliente ya estaban negados (verificado, 0 filas sin error) y ahora tienen su restrictive; `*_internal_all` intactas; grants de tabla y de secuencia acotados; las políticas legacy `*_service_only` se dejan (vestigiales, `service_role` tiene `BYPASSRLS`, predicado falso para anon/authenticated); `delivery_notes_issued` revisada, sin escritura de cliente, sin cambios (es E4 #29/#30).

---

## Qué se verificó y cómo

**Local, contra el stack real** (había Docker en el entorno — no hizo falta usar el CI como único oráculo):

- `supabase db reset` (las 26 migraciones + la nueva sobre DB vacía) + `supabase test db` → **`Files=8, Tests=99, Result: PASS`**. Las 19 nuevas pasan y ninguno de los 7 archivos preexistentes se rompió.
- Gate de tipos: `supabase gen types typescript --local --schema public` + `git diff --no-index --exit-code` contra `database.types.ts` → **sin drift**. La migración sólo toca políticas/grants/comentarios; nada que el generador emita. `database.types.ts` no se tocó a mano.
- `npm run typecheck` → 0 errores · `npx eslint src` → 0 errores (2 warnings preexistentes en `src/test/setup.tsx`) · `npm test` → **282/282 en 40 archivos**.
- La tabla "antes/después" de arriba es salida de comandos ejecutados como `authenticated`/`anon`, no inferencia.

**CI del PR**, run [`33184252265`](https://github.com/GuidoAmici/newhaze-webapp/actions/runs/33184252265) sobre `19c4c75`: los 8 jobs en verde, incluido `Migraciones → New Haze DB stg` — **la migración ya está aplicada en stg**.

### Dos ruidos del camino, ninguno del cambio

- **`E2E local` falló una vez y pasó al reintentar sin tocar nada.** Cayeron `tests-local/recovery.spec.ts:95` y `:116` (reset de contraseña). El mismo árbol ya había pasado ese job en el run anterior (`33183775765`). Un PR sólo-SQL no rompe el recovery de GoTrue: flake de ese spec. **Vale la pena vigilarlo** — es el segundo spec de recovery que da problemas de timing.
- **`Deployment de la integración Vercel` falló con `BLOCKED` en el primer push.** Causa: el commit salió con `user.email = newhazetek@gmail.com` (el email del perfil AWI) en vez del `user.email` local del repo (`guido@newhaze.ar`). Vercel no lo resolvió a un colaborador del proyecto — el deployment quedó sin `githubCommitAuthorLogin` y lo bloqueó por configuración de cuenta. Se rehízo el commit con la identidad del repo y pasó. **Lección para el harness AWI: en repos de cliente, el commit va con el `user.email` local del repo, no con el del perfil del usuario.** El email del perfil sirve para identificar al usuario, no para firmar commits en repos con integraciones que validan al autor.

---

## Fuera de alcance (detectado, no implementado)

- **El `GRANT ALL` sistémico del baseline legacy** — 41 tablas con `TRUNCATE` para `authenticated`. Es el follow-up que `rls_phase1.sql` ya se anotaba en su encabezado. Merece issue y PR propios: meterlo acá diluiría un cambio que tiene que ser chico y auditable de un vistazo.
- **La RPC de creación de pedidos, la columna de precio congelado y el piso G1** son #24. No se adelantaron.
- **`FORCE ROW LEVEL SECURITY`** sobre las dos tablas: rompería la RPC `SECURITY DEFINER` de #24. Descartado a propósito.
- **Las políticas legacy `*_service_only`**: inertes. Sacarlas es contracción sin ganancia.

---

## Resuelto por el maintainer (2026-08-28, tras entregar el PR)

Los cuatro puntos que quedaban para criterio humano volvieron resueltos:

1. **Corrección al `REVOKE` aceptada** — las políticas `RESTRICTIVE` quedan.
2. **E4 #28 va a escribir por RPC, no por tabla.** Anotado en un comentario de [#28](https://github.com/GuidoAmici/newhaze-webapp/issues/28#issuecomment-5457587146) para que quien lo tome no lo re-decida, con lo que eso habilita después: una vez desplegada esa RPC, ningún código escribe estas tablas como `authenticated` y entra el `REVOKE INSERT, UPDATE, DELETE … FROM authenticated` completo. **Con una salvedad que hay que no pasar por alto:** `sales_orders_internal_all` es `FOR ALL`, y su arm de `SELECT` es lo que le deja al panel interno leer **todos** los pedidos (`sales_orders_own_read` sólo cubre los propios y los de la org del usuario). No se borra: se achica a `FOR SELECT`. Es contracción → PR aparte, después del deploy (ADR-0017).
3. **`anon` pierde el `SELECT`** — **ya estaba en el PR desde el primer commit.** El `REVOKE ALL … FROM anon` de la línea 97 de la migración incluye `SELECT`, y el pgTAP lo cubre por partida doble: `throws_ok('SELECT 1 FROM public.sales_orders', '42501')` como `anon` y `NOT has_table_privilege('anon', …, 'SELECT')` sobre las dos tablas. No hizo falta commit nuevo; el PR sigue en `19c4c75` y en verde.

   Evidencia reforzada de que nada lo usa, pedida por el maintainer y ahora dura en vez de "no aparece en el grep": el universo **completo** de tablas que el código toca es `git grep -hoE '\.from\("[a-z_]+"\)' -- src` → `profiles` (6), `org_x_users` (6), `organizations` (3), `items` (2), `form_responses` (1). **`sales_orders`/`sales_order_items` no aparecen ni una vez, con ningún rol.** Y el único `createPublicClient()` (rol `anon`) del repo es `src/lib/catalog.ts:48`, que consulta `items`.
4. **Issue de las 41 tablas abierto: [#200](https://github.com/GuidoAmici/newhaze-webapp/issues/200)**, asignado a `senior-secops`, **sin empezar** por indicación explícita. Medido contra las bases reales y es peor de lo reportado acá: `anon` **también** tiene `TRUNCATE` — 38 tablas en stg, **40 en prod**, sobre 41.

**Dato de contexto del maintainer, medido con acceso directo:** prod tiene **0 organizaciones y 0 pedidos** (17 items). La superficie real de pedidos en producción está vacía — lo que refuerza la excepción a expand-only: la contracción se aplica sobre tablas que en prod no tienen ni una fila que perder.

## Qué queda abierto

- **PR #197 sin mergear**, esperando el merge del maintainer.
- **#200 sin empezar** (indicación explícita: primero cerrar #197).
- **El contrato que hereda #24:** con este PR la DB deja de validar pedidos del cliente por completo. El piso G1 y el recálculo server-side de precios viven enteros dentro de la RPC — si esa RPC los omite, no hay red abajo.
- **Vigilar `tests-local/recovery.spec.ts`**: es el segundo spec de recovery con flake de timing.

## Estado de gestión

- PR #197 **abierto** en `19c4c75`, sin mergear, CI entero en verde (run `33184252265`).
- Issue #193 comentado; labels: `en-pr` puesta, `ready-for-agent` sacada.
- Issue #28 comentado con la decisión de la RPC.
- Issue #200 recibido y **no empezado**, por indicación.
