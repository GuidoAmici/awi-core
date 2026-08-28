# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual label strings used in this repo's issue tracker.

| Label in skills | Label in our tracker | Meaning                                  |
| --------------- | -------------------- | ---------------------------------------- |
| `needs-triage`  | `needs-triage`       | Maintainer needs to evaluate this issue  |
| `needs-info`    | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent` | `ready-for-agent`  | Grilled, agent assigned in brief, ready for background delegation |
| `ready-for-human` | `ready-for-human`  | Requires human implementation            |
| `wontfix`       | `wontfix`            | Will not be actioned                     |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding label string from this table.

Edit the right-hand column to match whatever vocabulary you actually use.

## Estados de ciclo de vida (agregado 2026-08-28)

`ready-for-agent` significa «listo para despachar», no «alguien lo está haciendo». Un issue con un PR abierto que lo implementa sigue apareciendo en el scan de `/delegate-issue` y se puede re-despachar, duplicando trabajo. Caso real: `newhaze-webapp#21` y `#25` estuvieron dos días con PR verde sin mergear y con el label puesto.

Los PRs se abren contra `stg`, no contra producción, así que mergear no es publicar. El ciclo tiene tres estados, no dos:

| Label | Significado | Quién lo pone / saca |
|---|---|---|
| `en-pr` | Implementado en un PR abierto contra `stg`. **No re-delegar hasta que mergee.** | Lo pone quien abre el PR (o quien detecta el PR); lo saca el merge. |
| `en-stg` | Mergeado a `stg`. El issue ya está cerrado, pero el usuario final todavía no lo tiene. | Lo pone el merge; lo saca la promoción a prod. |
| `en-prod` | Cerrado **y** promovido a producción — no sólo mergeado a stg. | Lo pone la promoción `stg → prod`. |

Regla para `/delegate-issue`: un issue con `en-pr` **nunca** es elegible, aunque tenga `ready-for-agent`. Al abrir un PR que implementa un issue, sacar `ready-for-agent` y poner `en-pr`.

En `newhaze-webapp` el paso a `en-prod` se automatiza en `release-prod.yml` (PR #173). El paso a `en-stg` es el mismo gesto en `stg-ci.yml` y conviene automatizarlo junto: un label de ciclo de vida que depende de que alguien se acuerde de ponerlo no es un estado, es una intención.
