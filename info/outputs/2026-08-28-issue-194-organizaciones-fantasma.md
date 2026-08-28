# #194 — Organizaciones fantasma reclamables

**Fecha:** 2026-08-28 · **Empleado:** `backend-architect` · **PR:** [newhaze-webapp#198](https://github.com/GuidoAmici/newhaze-webapp/pull/198) (contra `stg`, sin mergear)
**Rama:** `docs/194-organizaciones-fantasma`

---

## TLDR

El issue pedía traer el histórico de ventas a la base contra organizaciones fantasma reclamables. **Al contrastarlo contra el esquema, resultó que el import ya se hizo en julio: las fantasma existen, el histórico ya cuelga de ellas, y están en el estado peligroso (`approved`).** Lo urgente no era importar sino ponerle candado a lo importado — y ese candado cierra una exposición que ya está abierta hoy, no una futura.

Entregado: ADR-0022, dos migraciones aditivas, 31 assertions de pgTAP (verdes), el script de reclasificación y el plan del import. Nada ejecutado sobre datos productivos.

**Segundo hallazgo, del CI:** el job de migraciones falló porque mis timestamps colisionaron con los de #193, y `db-push.mjs` **se saltaba la migración duplicada en silencio**. El stack local no puede ver ese modo de falla. stg quedó intacta; el detalle está más abajo, y es lo más reutilizable de todo este trabajo.

---

## Lo que encontré antes de diseñar

Tres hechos que cambian la forma del trabajo:

1. **Las fantasma ya existen.** `supabase/import/transform.sql:136` las creó en el import de #43 — una fila de `organizations` por cliente legacy, deduplicada por nombre normalizado. Son las 53 que menciona el comentario de `20260716160000_approve_organization.sql`.
2. **El histórico ya cuelga de ellas.** `transform.sql:162` ya corrió el `UPDATE sales_orders SET org_id = ...` matcheando por nombre normalizado, y lo mismo con `invoices` y `receipts`.
3. **Y están en `approved`.** `transform.sql:139` las insertó así. `org_x_users_internal_all` (`rls_phase1.sql:167`) es `FOR ALL`: **cualquier empleado puede insertar una membresía en cualquier organización.** Una fila mal puesta en el panel interno alcanza para que una persona vea el historial completo de un comercio ajeno (`sales_orders_own_read`, `invoices_counterparty_read`, `receipts_counterparty_read`) y además herede su tier B2B, porque `private.my_tiers()` filtra por `status = 'approved'`.

O sea: **el riesgo que el issue proyecta hacia el futuro del acto de fusión ya está abierto**, y el estado `approved` de las fantasma es lo que lo mantiene abierto.

Cuarto hallazgo, del lado de prod: `rbszz` tiene 17 items (ADR-0012 §5), el histórico referencia ~300, y `sales_order_items.item_id` es `NOT NULL` con FK a `items`. **El histórico no entra a prod hasta que entre el catálogo completo.** Eso mantiene el diferimiento de ADR-0012 §1 para prod, ahora por un bloqueo técnico concreto y no por prioridad.

---

## La recomendación

| Pieza | Qué es |
|---|---|
| Estado `unclaimed` | La cola de triaje. `WHERE status = 'unclaimed'` — sin tabla ni flag aparte. |
| Estado `merged` | Lápida. **No se borra**: es lo que mantiene idempotente a `transform.sql` (que evita recrear por `NOT EXISTS ... norm(name)`) y el único registro de que la fusión ocurrió. |
| Trigger en `org_x_users` | **La invariante que sostiene todo.** Una fantasma no admite miembros — ni desde el panel interno, ni desde `service_role`. Con eso, el RPC de fusión es el *único* camino por el que el histórico cambia de manos. |
| `merge_unclaimed_organization` | Solo `newhaze_admin`; destino `approved` con owner; CUIT no contradictorio sin override; confirmación **por transcripción**. |
| `preview_organization_merge` | Dry-run de solo lectura. Es lo que evita el error; el guard solo lo ataja. |
| `merged_from_org_id` + `organization_merges` | Provenance en cada fila movida → reversión exacta, sin ventana de tiempo. |

**Dirección de la fusión:** sobrevive la org que el comercio registró y un empleado aprobó. La fantasma cede su historia y se apaga.

**Confirmación por transcripción, no booleana:** el modo de falla real es elegir la fantasma equivocada entre 53 nombres parecidos, y un `p_confirm := true` no lo atrapa — se defaultea y se clickea sin leer. Transcribir el CUIT (o el nombre) de la fila que se va a disolver hace que un `p_ghost` errado falle cerrado. Patrón «escribí el nombre del repo para borrarlo».

**La reversión repara los datos, no la confidencialidad.** Lo que el comercio equivocado vio, ya lo vio. Por eso el peso está en el guard preventivo.

---

## Alternativas descartadas, y por qué

| Alternativa | Por qué no |
|---|---|
| **Fundir al revés** (la fantasma sobrevive y adopta al comercio) | Más barata en filas movidas, pero resucita identidad legal no corroborada **y la congela** —ADR-0014 bloquea `name`/`cuit`/`type` una vez `approved`—, descarta el `approved_by`/`approved_at` que es el único acto de verificación que hubo, y es irreversible. |
| **Reclamo autoservicio** (el comercio prueba su CUIT) | Convierte un dato semi-público en la llave de lectura del historial comercial ajeno. El costo de la alternativa es una intervención humana por comercio, sobre 53, una sola vez. |
| **Borrar la fantasma tras fundir** | `transform.sql` la recrea en la próxima corrida (idempotencia por nombre normalizado) y se pierde el registro de la fusión. |
| **Bolsa común de clientes legacy** | Ya descartada en el issue; además haría imposible el guard de transcripción (no habría identidad que transcribir). |
| **Nivel empleado para fundir**, como `approve_organization` | Aprobar corrobora los datos de *una* org; fundir expone el historial de A a los miembros de B. Escalada deliberada a admin. |
| **Endurecer `org_x_users_internal_all`** en vez del trigger | Es `FOR ALL`: reescribirla toca el permiso de escritura del equipo entero por un caso de borde. El trigger es transversal, un solo punto, un solo test. |
| **Estado `historico` en `sales_orders`** | `imported_at` ya cumple ese rol (ADR-0005 §4). Un cuarto valor obligaría a cada consumidor de `status` a aprender un valor que significa «no aplica». |
| **Tabla puente fantasma ↔ comercio** | `sales_orders.org_id` ya es FK a `organizations`. |
| **Matching con IA escribiendo la fusión** | Aceptado como insumo del `preview` (propuestas con evidencia), nunca como escritura. |
| **La reclasificación como migración** | Es dato, no esquema. Va como script en `supabase/import/`, con la misma división que el repo ya usa entre `import_finalize` y `transform.sql`. |

---

## El bug que encontró el propio pgTAP

Escribí el guard de admin como `IF (SELECT private.internal_role()) <> 'newhaze_admin' THEN RAISE ...`. **No dispara.** `internal_role()` devuelve `NULL` para quien no es del equipo, `NULL <> 'texto'` es `NULL`, y un `IF` con `NULL` no entra en la rama: la fusión pasaba sin ser admin. El test «sin sesión no se funde» lo cazó en la primera corrida (`caught: no exception`). Corregido con `IS DISTINCT FROM`.

Vale como regla general para el repo: `approve_organization` no tiene el problema porque usa `is_internal()`, que devuelve boolean, y las políticas RLS tampoco porque ahí `NULL` se evalúa como falso. **La trampa es exclusiva de la negación dentro de plpgsql** — conviene revisar cualquier RPC futuro que compare `internal_role()` con `<>`.

---

## Qué queda pedido al maintainer

1. **¿Se mueve el `balance_ars` de la fantasma al comercio?** Sale de `ListaClientes`, frescura desconocida. Hoy el RPC lo suma y lo registra para poder restarlo al revertir; la alternativa es fundir con 0 y reconciliar desde `receipts`. Cambia una línea.
2. **¿`confirmado` como estado del histórico cierra?** Se mantiene el mapeo del import. El costo: `confirmado` en una fila legacy significa «esta venta ocurrió», no «un empleado la confirmó», y el panel de E4 va a tener que filtrar `imported_at IS NULL`.
3. **¿La reclasificación fuera de las migraciones está bien?** Va como script con gate propio (aborta si alguna org del import ya tiene miembros).
4. **GSG: ¿es una fantasma o varias?** El dedupe por nombre normalizado pudo dejar «GSG», «G.S.G.» y «Growshop GSG» como tres orgs con tres pedazos de historia. La Fase 0 del plan lo contesta y hay que contestarla antes de la primera fusión.
5. **El `type` que GSG elija tiene que coincidir con el de su fantasma**, y hay que verificarlo **mientras la org está `pending`**: una vez `approved`, `type` queda bloqueado (ADR-0014) y el tier de precios queda mal.
6. **Quién de GSG queda como owner.** El historial completo se le entrega al owner de la org destino.
7. **El experimento de alta y la fusión son separables, y el de alta va primero.** Medir si el principal canal se registra solo necesita el flag `orgs` en **ON** en prod (hoy OFF, ADR-0012 §5) y no necesita nada del histórico; la fusión en prod está bloqueada por el catálogo. Sugerencia: correr el alta de GSG ya y ensayar la fusión en `stg`, que es donde está la historia.

---

## El fallo de CI, y lo que enseña sobre verificar migraciones

**Mi verificación local dio verde sobre algo que el push a stg rechaza.** Vale anotarlo, porque le va a pasar a cualquiera.

### Qué pasó

El job `Migraciones → New Haze DB stg` del PR falló con:

```
ERROR: 42P01: relation "public.organization_merges" does not exist
CONTEXT: compilation of PL/pgSQL function "revert_organization_merge" near line 3
```

La tabla la crea mi primera migración y la función vive en la segunda. En el log del job hay **una sola** línea `Aplicando …`, la de la segunda: **la primera nunca se intentó.**

Causa: elegí `20260828120000` como timestamp, el mismo que `pedidos_sin_insert_directo` de #193 (PR #197), que ADR-0017 ya había aplicado a stg pre-merge. `scripts/db-push.mjs` indexa el historial por **version** (el timestamp), no por nombre de archivo:

```js
const version = f.split('_')[0];
if (remote.has(version)) continue;   // ← se la saltó en silencio
```

Vio `20260828120000` presente y se saltó mi archivo **sin decir nada**. La segunda migración corrió contra una base donde la tabla nunca se creó.

### Por qué el stack local no lo cubre

Son dos caminos distintos y sólo uno es el real:

| | `supabase db reset` (local, y el job `pgtap`) | `db-push.mjs` (stg y **prod**) |
|---|---|---|
| Contra qué corre | Una DB **vacía** | Una DB **con historial** |
| Qué aplica | **Todos** los archivos del directorio | Sólo los que faltan **según el historial** |
| Identidad de una migración | El archivo | **El timestamp, sin el nombre** |
| Ve las migraciones de otros PRs abiertos | No | **Sí** (stg es compartida, ADR-0017) |

Una colisión de timestamp es **invisible en local por construcción**: no hay historial que consultar. El local siempre iba a dar verde.

### Lo grave no es que fallara, es que casi no falla

Se descubrió **de casualidad**: mi segunda migración declara `v_m public.organization_merges%ROWTYPE`, y `%ROWTYPE` se resuelve al compilar la función, así que explotó. **Si las dos migraciones no hubieran estado acopladas, el run quedaba VERDE con la primera nunca aplicada a stg** — divergencia silenciosa entre los archivos y la base, arrastrada hasta prod por el mismo script.

Con stg compartida pre-merge entre todos los PRs abiertos (ADR-0017), la colisión no es rara: es lo esperable cualquier día con dos ramas activas, porque todo el mundo tipea un `HHMMSS` redondo como `120000`. Ese día era hoy y las ramas eran #193 y #194.

### Qué hice

1. **Renombré mis migraciones** a `20260828154500` / `20260828154600` (verificados libres contra las seis ramas abiertas con migraciones).
2. **`db-push.mjs` guarda ahora el `name` además de la `version` y falla fuerte** cuando una version ya registrada corresponde a otro archivo, con un mensaje que dice qué renombrar. Detección pura: no cambia la semántica de aplicación, sólo convierte en rojo lo que hoy es silencio. **Va marcado aparte en el PR** — si preferís que salga en su propio PR, se saca en un commit.

### Estado de stg: intacta, verificado

La llamada de la migración fallida es transaccional, así que no quedó nada suelto. Contra `rpgoix`:

| Verificación | Resultado |
|---|---|
| `organization_merges`, `merged_into_org_id`, `merged_from_org_id`, el trigger, y las 4 funciones | **ninguno existe** |
| `organizations_status_check` | `CHECK (status = ANY (ARRAY['pending','approved']))` — **el original**, mi `DROP CONSTRAINT` nunca corrió |
| `schema_migrations` en `20260828120000` | una sola fila: `pedidos_sin_insert_directo` (#193) |
| Orgs | 54 total, 53 fantasma en `approved`, **0** en estado nuevo |

**No hay nada que limpiar en stg.** El fallo fue *fail-closed*.

### Efecto sobre las seis decisiones abiertas

**Ninguna cambia.** El arreglo es de fontanería (nombre de archivo + guard del runner); no toca el diseño, ni los guards de la fusión, ni el plan del import.

## Verificación

- `supabase db reset` desde cero: 25 migraciones aplican limpio.
- `supabase test db`: `All tests successful. Files=8, Tests=111` — 31 assertions nuevas, 80 preexistentes intactas.
- `src/lib/supabase/database.types.ts` regenerado desde el stack local (+132 líneas, aditivas): el job `pgtap` compara commiteado vs. migraciones y pasa.
- No se ejecutó ningún import ni se tocó `stg` ni `prod` a mano. Por ADR-0017, abrir el PR aplica las migraciones a `stg` — son aditivas y no cambian ninguna fila (sin fantasmas marcadas, el trigger y los CHECKs son no-ops). Está declarado arriba de todo en el PR.
- **El oráculo es el CI, no el stack local.** El local corre contra una DB vacía sin historial y sin las migraciones de los otros PRs abiertos; el job `migrate-stg` corre el camino real. Lo aprendí por las malas en este mismo PR (ver arriba).

## Archivos

- `docs/adr/0022-organizaciones-fantasma-reclamables-y-acto-de-fusion.md`
- `supabase/migrations/20260828154500_unclaimed_organizations.sql`
- `supabase/migrations/20260828154600_merge_unclaimed_organization.sql`
- `supabase/tests/unclaimed_organizations_test.sql`
- `supabase/import/reclassify_unclaimed.sql`
- `src/lib/supabase/database.types.ts` (regenerado)
- `scripts/db-push.mjs` (guard de colisión de timestamp)
