---
tipo: agentes
capa: operacion
descripcion: Un PR con migración contra stg de newhaze-webapp la aplica a stg al abrirse; se avisa al operador antes de abrirlo.
last-updated: 2026-10-06
---

# Migraciones en un PR: se avisa antes de abrirlo

**Regla (2026-10-06, confirmada por el operador).** En `newhaze-webapp`, un PR con migración contra `stg` **la aplica a la base de stg en cuanto se abre**. Se puede hacer, pero quien lo abre **avisa al operador antes**, no después. El aviso va por el Chief of Staff (o por el chat, si el operador está en la sesión).

## Por qué

El job `migrate-stg` de `.github/workflows/stg-ci.yml` corre también en `pull_request` (el preview de Vercel del PR apunta a la DB de stg y necesita ver el schema del PR sin esperar el merge). El 2026-10-05, al abrir el PR de la tabla `feedback_juego` (webapp#278), la migración se aplicó a stg antes de que nadie la mergeara, y el operador se enteró después. La regla "nada se aplica al Supabase remoto sin su OK" no contemplaba que abrir un PR ya lo hace.

## Qué cubre y qué no

- **stg:** se aplica al abrir el PR. Contrato **expand-only**: sólo agrega (tabla, columna nullable, RPC). Nunca `drop`, `rename` ni `NOT NULL` sin default.
- **prod:** no cambia. Una migración sólo llega a producción por `release-prod.yml`, que frena si el diff `prod..stg` trae migraciones y espera a un humano.
- **Un PR cerrado sin mergear** deja su tabla o función en stg. Se limpia a mano, con el OK del operador.

## Dónde más está escrita

- `AGENTS.md` de `newhaze-webapp`, bajo "Convención de Pull Requests" (webapp#277).
- Un subagente que va a abrir un PR con migración se lo escala a `main`; `main` avisa al operador antes de que se abra. El brief lo dice.
