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

## Qué necesita ojo humano

1. **¿Se acepta la corrección al `REVOKE`?** Es el punto donde el PR se aparta de lo pedido en el issue.
2. **¿E4 #28 va a escribir pedidos como interno `authenticated` (por tabla) o por RPC?** Si el plan real es RPC también para el panel interno, entonces sí se puede hacer el `REVOKE` completo a `authenticated` y eso es una capa más. Es decisión de E4.
3. **¿`anon` puede perder el `SELECT` sobre pedidos?** Verificado que nada en este repo lo usa; queda el ojo humano por consumidores externos (scripts, dashboards).
4. **¿Se abre el issue por las 41 tablas con `TRUNCATE`?**
5. **Recordatorio del contrato:** con este PR la DB deja de validar pedidos del cliente por completo. **El piso G1 y el recálculo server-side de precios pasan a vivir enteros dentro de la RPC de #24** — si esa RPC los omite, no hay red abajo.

## Estado de gestión

- PR #197 **abierto**, sin mergear, como pedía el issue.
- Issue #193 comentado; labels: `en-pr` puesta, `ready-for-agent` sacada.
