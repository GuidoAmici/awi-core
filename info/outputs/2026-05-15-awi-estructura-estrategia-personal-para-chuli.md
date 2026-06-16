---
type: reference
audience: chuli
date: 2026-05-15
topic: estructura del manifiesto de estrategia personal por organización en AWI
---

# Estructura del manifiesto de estrategia personal por organización (AWI)

Esta guía documenta cómo está organizada la planificación estratégica personal de Guido en AWI, para que puedas replicar la misma estructura en tu propia instancia.

---

## Concepto central

La estrategia personal no vive en un solo archivo. Está distribuida en capas:

```
agenda/projects/<cross-org-strategy>.md   ← manifiesto transversal (el "por qué" entre orgs)
agenda/planning/YYYY-annual.md            ← visión y objetivos del año completo, por org
agenda/planning/YYYY-QN.md               ← plan trimestral con deliverables concretos
agenda/weekly/YYYY-WNN.md                ← selección semanal + pulso de estado
agenda/daily/YYYY-MM-DD.md              ← sesión diaria
agenda/companies/<NombreOrg>.md          ← ficha de la organización (contexto y gente)
agenda/projects/<nombre-proyecto>.md     ← un proyecto que cruza o involucra varias orgs
```

---

## Archivo 1 — Manifiesto transversal (projects/)

**Propósito:** documenta la estrategia que conecta todas tus organizaciones. Responde "¿cuál es el juego grande y en qué orden avanzo?"

**Ruta:** `agenda/projects/saas-vertical-strategy.md` *(ejemplo de Guido)*

**Frontmatter:**
```yaml
---
type: project
status: active
tags: [strategy, <org1>, <org2>, <org3>]
last-updated: YYYY-MM-DD
---
```

**Estructura del cuerpo:**

```markdown
# <Nombre de la estrategia> — <N>-Org Initiative

<Una oración: cuál es la apuesta estratégica global>

## The Sequence

1. **<Org A>** — <por qué va primero y qué produce>
2. **<Org B>** — <cómo se apoya en el resultado de A>
3. **<Org C>** — <el producto final o la síntesis>

## Why This Order

<3-4 oraciones explicando la lógica del orden>

## Underlying Principle

<La idea que da coherencia al sistema>

## Orgs Involved

- [[companies/<OrgA>]] — <rol> → [[<org>:projects/<proyecto>]]
- [[companies/<OrgB>]] — <rol> → [[<org>:projects/<proyecto>]]
- [[companies/<OrgC>]] — <rol>

## Operating Rules

Decisiones permanentes — no re-derivar cada semana.

1. **<Regla 1>** — <descripción>
2. **<Regla 2>** — <descripción>
3. **<Regla 3>** — <descripción>

## Next Actions

- [ ] <tarea concreta pendiente>
- [ ] <tarea concreta pendiente>
```

---

## Archivo 2 — Plan anual (planning/)

**Propósito:** visión del año + objetivos numerados + roadmap por cuatrimestre + dependency chain.

**Ruta:** `agenda/planning/YYYY-annual.md`

**Frontmatter:**
```yaml
---
type: annual
year: YYYY
last-updated: YYYY-MM-DD
---
```

**Estructura del cuerpo:**

```markdown
# YYYY Annual Plan

## Vision

<1-2 párrafos: qué significa este año en términos de identidad y posición>

---

## Monetization Philosophy (si aplica)

<Cómo piensas el dinero este año: modelo, métricas clave, hipótesis a probar>

---

## Goals

1. **<Meta 1>** — <descripción>
   - Key projects: [[<proyecto>]]
   - Target quarter: Q<N>
   - Blocked by: <dependencia o "nothing">

2. **<Meta 2>** — ...

---

## Q1 (Jan–Mar) — <Tema del cuatrimestre>

### Theme: <Una palabra o frase>

<Qué define este bloque de tiempo>

- [[<proyecto>]] — <entregable clave>
- [[<proyecto>]] — <entregable clave>

### Key deliverables
- <entregable 1>
- <entregable 2>

---

## Q2, Q3, Q4 — (mismo patrón)

---

## Parking Lot

- <Cosa que NO entra este año pero no se descarta>

---

## Dependency Chain

\```
<proyecto raíz>
└── <dependencia>
    ├── <sub-dependencia>
    └── <sub-dependencia>
\```
```

---

## Archivo 3 — Plan trimestral (planning/)

**Propósito:** objetivos del trimestre, tareas completadas, tareas abiertas, parking lot y deferrals al siguiente trimestre.

**Ruta:** `agenda/planning/YYYY-QN.md`

**Frontmatter:**
```yaml
---
type: quarterly
quarter: YYYY-QN
date-range: YYYY-MM-DD to YYYY-MM-DD
product: <org-principal>
last-updated: YYYY-MM-DD
---
```

**Estructura:**
```markdown
# QN YYYY

<Una oración: el objetivo central del trimestre>

## Goals

1. **<Objetivo 1>** — descripción
   - Project: [[<proyecto>]]
   - Task: [[<tarea>]]

---

## <Mes 1>

### Projects
- **<proyecto>** — qué se hizo

### Tasks
- [x] tarea completada
- [ ] tarea pendiente

---

## (Meses 2 y 3, mismo patrón)

---

## Parking Lot

| Item | Status | Notes |
|------|--------|-------|
| <feature> | pending | <contexto> |

---

## Q<N+1> Deferrals

| Initiative | Reason | Revisit |
|------------|--------|---------|
| <iniciativa> | <por qué se defer> | Q<N+1> |
```

---

## Archivo 4 — Plan semanal (weekly/)

**Propósito:** selección de tareas de la semana, backlog excluido, estado de proyectos activos y pulso al cierre.

**Ruta:** `agenda/weekly/YYYY-WNN.md`

**Frontmatter:**
```yaml
---
type: weekly
week: YYYY-WNN
status: reviewed
---
```

**Estructura:**
```markdown
# Week NN — <Fecha inicio>–<Fecha fin>, YYYY

## Mental Model of the Week

[[mental-models/<modelo>]] — <Una oración sobre el foco de la semana>

## Selected for This Week

| Task | Priority | Energy | Duration | Due |
|------|----------|--------|----------|-----|
| <repo>#<num> — <descripción> | high/medium/low | high/medium/low | Xh | <fecha o ASAP> |

**Total estimated time:** ~Xh
**Available time (5 days):** ~Xh

**The bet this week:** <una oración de apuesta>

## Backlog (not selected)

- <repo>#<num> — <descripción> (<razón de exclusión>)

## Carried Over

- **<repo>#<num>** — slip de cuántos días + causa + resolución

## Active Projects — Status

- **<Proyecto>** — estado actual y foco de la semana

## Week Pulse

> Actualizado al cierre del <día>.

<N> de <M> tareas seleccionadas cerradas. <Descripción de lo que ocurrió realmente.>
```

---

## Archivo 5 — Ficha de organización (companies/)

**Propósito:** contexto estático de cada empresa u organización con la que trabajás.

**Ruta:** `agenda/companies/<NombreOrg>.md`

**Frontmatter:**
```yaml
---
type: company
tags: [client/partner/own, <categoría>]
last-contact: YYYY-MM-DD
---
```

**Estructura:**
```markdown
# <Nombre de la Org>

<1-2 oraciones de descripción>

## People
- [[people/<Nombre>]] — rol

## Infrastructure (si aplica)
- <recurso técnico relevante>

## Relationship
- Tipo de relación
- Ver [[projects/<nombre-proyecto>]]
```

---

## Cómo se interconectan

```
saas-vertical-strategy.md
  └── agenda/companies/NewHaze.md          ← quién es la org
  └── agenda/projects/newhaze-full-system  ← qué se está construyendo
  └── agenda/planning/2026-annual.md       ← visión del año
        └── agenda/planning/2026-Q2.md     ← objetivos del trimestre
              └── agenda/weekly/2026-W20.md ← selección de la semana
                    └── agenda/daily/2026-05-14.md ← sesión diaria
```

---

## Convenciones de links

- `[[companies/NombreOrg]]` — referencia a una ficha de organización
- `[[projects/nombre-proyecto]]` — referencia a un proyecto
- `[[<org>:projects/<proyecto>]]` — proyecto específico de una organización
- `[[outputs/YYYY-MM-DD-nombre]]` — documento de salida generado en una sesión

---

## Herramienta de apoyo

AWI incluye skills para operar sobre esta estructura:

- `/today` — abre o continúa la sesión diaria
- `/week` — muestra el plan semanal activo
- `/quarter` — muestra el plan trimestral
- `/year` — muestra el plan anual
- `/new` — crea un nuevo item (task, project, idea, etc.)
- `/history` — actividad reciente de git

Estos skills funcionan porque la estructura de carpetas es consistente. Si replicás exactamente la jerarquía descripta arriba, todos los skills funcionarán igual en tu instancia.
