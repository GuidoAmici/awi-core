# Issue tracker: GitHub (multi-repo)

Issues live in GitHub Issues, distributed by scope. Use the `gh` CLI for all operations. Always pass `--repo` explicitly.

## Where issues live

**Los issues de código viven en el repo del código; los workspace repos son solo para negocio, proyectos y decisiones.** (Convención corregida por el maintainer el 2026-07-16 — reemplaza a la regla anterior "never in codebase repos".)

| Scope | Repo | When to use |
|-------|------|-------------|
| Código (features, bugs, tests, deuda técnica) | El repo del codebase (e.g. `GuidoAmici/newhaze-webapp`) | Todo lo que se implementa en ese repo: features de app, fixes, infraestructura de tests, refactors. Ejemplos reales: variantes de producto (`newhaze-webapp#63`), pgTAP (`#65`), E2E (`#66`). |
| Negocio / proyectos / decisiones de una org | `GuidoAmici/newhaze-workspace`, `GuidoAmici/afin-workspace`, `GuidoAmici/rabbitek-workspace` | Estrategia, pricing, lanzamientos (BDR), operaciones, tareas humanas, épicas cross-repo. Ejemplos reales: promos de lanzamiento (`newhaze-workspace#90`), packs en el sheet (`#61`). Label `repo:<codebase>` si referencia código. |
| AWI harness | `GuidoAmici/awi-core` | Changes to the AWI system itself: skills, CLAUDE.md, hooks, documentation standards, agent behavior. |
| Personal | `GuidoAmici/my-awi-user` | Strictly personal work (agenda, goals, personal projects). Never for harness or cross-org work. |

Regla rápida: si lo cierra un PR, va en el repo del código; si lo cierra una decisión o una acción humana, va en el workspace. Cuando toca codebases de varias orgs, preguntar al maintainer en qué workspace filearlo.

## Label schema

| Dimension | Examples |
|-----------|---------|
| Org | `org:newhaze`, `org:afin`, `org:rabbitek` — applied to every issue regardless of repo. Enables cross-repo filtering and local (off-GitHub) issue management by org. |
| Codebase | `repo:newhaze-b2b-panel`, `repo:newhaze-api`, `repo:newhaze-ui` |
| Project | `project:ci-cd-pipeline`, `project:sso` (matches `agenda/projects/*.md` slug) |
| Triage | see `docs/agents/triage-labels.md` |

Apply multiple labels when an issue spans repos or projects.

## Milestones

One GitHub Milestone per AWI project (`agenda/projects/*.md`). Create in the relevant org workspace repo. Slug matches the project filename (e.g. `ci-cd-pipeline`).

## Conventions

- **Create**: `gh issue create --repo <owner/repo> --title "..." --body "..."`
- **Read**: `gh issue view <number> --repo <owner/repo> --comments`
- **List**: `gh issue list --repo <owner/repo> --state open --json number,title,body,labels --label "..."`
- **Label**: `gh issue edit <number> --repo <owner/repo> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --repo <owner/repo> --comment "..."`

## When a skill says "publish to the issue tracker"

Always ask the maintainer where to file before creating an issue. Suggest a destination based on scope:

1. One codebase → suggest that codebase's **org workspace repo**, labeled `repo:<codebase>`
2. One org, multiple codebases → suggest that org's workspace repo
3. AWI harness change (skill, hook, CLAUDE.md, doc standard) → `GuidoAmici/awi-core`
4. Personal → `GuidoAmici/my-awi-user`

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --repo <owner/repo> --comments`. Infer the repo from context — label, project, or codebase being worked on.

## When to prefer MCP over `gh` CLI

- **Multi-repo queries**: fetching issues from several repos in parallel — one MCP call per repo vs. one `gh` subprocess per repo.
- **Structured data**: MCP returns typed JSON; `gh` output requires parsing.
- **Background agents**: MCP tools have no shell overhead and fewer permission prompts.

For file system operations (clone, checkout, push) and `gh auth` management, continue using `gh` CLI directly.

## Closing the loop on issues

When work resolves, supersedes, or invalidates a tracked issue — in **any** repo, not just the one being worked on — **always comment on the issue and offer to close it**. Never close silently, and never leave a resolved issue open without a comment.

The comment must state:

1. **What changed** — the commit SHA, PR, or ADR that resolved it
2. **Why it resolves the issue** — or, if the issue no longer applies, what made it moot
3. **What remains**, if anything — link a follow-up issue rather than leaving the original half-done

**Suggest the close, don't just offer it.** When the evidence points one way, say so and recommend the disposition — `completed`, `not planned`, or stay open — with the reason. A neutral "should I close this?" pushes back onto the operator work the agent already did. The operator accepts, corrects, or rejects; the agent never closes on its own unless asked.

Before starting non-trivial work, search the issue trackers for prior art — issues frequently record decisions that an ADR later formalised, and acting without reading them risks contradicting a decision already made.

## Qué está en juego y qué duerme

El tracker no distingue lo que está en curso de lo que espera. Los labels de triage dicen en qué punto de la evaluación está un issue, no si alguien lo va a tocar esta semana, y `priority:` está poblado donde el operador prioriza a mano y vacío en el resto. Esa distinción hay que **derivarla**, no esperarla del tracker.

En orden, un issue está en juego si:

1. **El operador lo nombró** en esta sesión, en el daily o en el plan de la semana. Manda sobre todo lo demás.
2. **Está triado y listo** — `ready-for-agent` o `ready-for-human`. `needs-triage` y `needs-info` significan que todavía no se decidió nada.
3. **Tiene prioridad, assignee o milestone puestos.** Cuando el operador se tomó el trabajo de marcarlo, es señal. La ausencia no significa "baja" — significa **sin clasificar**, y hay trackers enteros sin clasificar.
4. **Se movió hace poco** — comentarios o cambios en las últimas dos semanas.
5. **Toca lo que estás haciendo ahora**, aunque nada de lo anterior aplique.

Lo demás es backlog: sigue abierto, no está en juego hoy.

### Qué traer

Traé enteros los que están en juego y los que toca la tarea. Del resto alcanza con saber que existen — y decí cuántos dejaste afuera, para que el operador pueda pedirlos.

**La excepción es real y hay que reconocerla:** en trabajo de estrategia o arquitectura, el barrido completo *es* el trabajo — un backlog leído a medias produce un diseño que ignora la mitad de las restricciones. Ahí se trae todo, y se dice que se hizo y por qué.

Esto decide qué entra en la conversación, no relaja nada de la sección anterior: cualquier identificador que menciones, del backlog o no, se lee antes de nombrarlo.

## Migration note

`agenda/tasks/` files are retired. Do not create new files there. Actionable work goes to GitHub Issues.
`agenda/projects/` files are kept — they are context/scope documents, not issue lists.
