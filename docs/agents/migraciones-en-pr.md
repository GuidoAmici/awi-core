---
tipo: agentes
capa: operacion
descripcion: Un PR con migración contra stg de newhaze-webapp la aplica a stg al abrirse. La expand-only no pide aviso; la que no lo es, pide el OK del operador antes de abrir el PR.
last-updated: 2026-10-10
---

# Migraciones en un PR: qué pide el OK del operador

**Regla (2026-10-10, confirmada por el operador; reemplaza a la del 2026-10-06).** En `newhaze-webapp`, un PR con migración contra `stg` **la aplica a la base de stg en cuanto se abre**.

- **Expand-only** (sólo agrega, según las reglas R1–R10 del ADR-0029 de la webapp): se abre sin aviso previo. Si además pasan los demás gates, el agente mergea el PR a stg él mismo (sección «Merge a stg» del `AGENTS.md` de la webapp).
- **No expand-only** (`DROP`, `UPDATE`/`DELETE` de datos, cambios de permisos o de cuerpo sobre objetos que ya existen, `setval`): **no se abre** hasta que el operador lo apruebe. El pedido va por el Chief of Staff, que lo junta con los demás.

## Por qué cambió

Hasta el 2026-10-10 toda migración pedía aviso previo, y los PRs se trababan esperando al operador. El operador aprobó que el merge a stg no lo espere cuando pasan los gates, y prueba stg con todo junto en vez de PR por PR. El aviso queda para lo que puede romper algo que ya existe.

El job `migrate-stg` de `.github/workflows/stg-ci.yml` corre también en `pull_request`: el preview de Vercel del PR apunta a la DB de stg y necesita ver el schema del PR sin esperar el merge. Eso es lo que hace que abrir el PR ya aplique la migración (pasó con `feedback_juego`, webapp#278, el 2026-10-05).

## Qué cubre y qué no

- **stg:** se aplica al abrir el PR.
- **prod:** no cambia. Una migración sólo llega a producción por `release-prod.yml`, con un backup local verificado antes.
- **Un PR cerrado sin mergear** deja su tabla o función en stg. Se limpia a mano, con el OK del operador.

## Dónde más está escrita

- `AGENTS.md` de `newhaze-webapp`, secciones «Convención de Pull Requests» y «Merge a stg» (webapp#306).
- Un subagente que va a abrir un PR con una migración que no es expand-only se lo escala a `main`, y `main` al Chief of Staff. El brief lo dice.
