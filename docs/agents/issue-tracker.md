# Issue tracker: GitHub (multi-repo)

Issues live in GitHub Issues, distributed by scope. Use the `gh` CLI for all operations. Always pass `--repo` explicitly.

## Where issues live

**Los issues de código viven en el repo del código; los workspace repos son solo para negocio, proyectos y decisiones.** (Convención corregida por el maintainer el 2026-07-16 — reemplaza a la regla anterior "never in codebase repos".)

| Scope | Repo | When to use |
|-------|------|-------------|
| Código (features, bugs, tests, deuda técnica) | El repo del codebase (e.g. `GuidoAmici/newhaze-webapp`) | Todo lo que se implementa en ese repo: features de app, fixes, infraestructura de tests, refactors. Ejemplos reales: variantes de producto (`newhaze-webapp#63`), pgTAP (`#65`), E2E (`#66`). |
| Negocio / proyectos / decisiones de una org | `GuidoAmici/newhaze-workspace`, `GuidoAmici/afin-workspace`, `GuidoAmici/rabbitek-workspace` | Estrategia, pricing, lanzamientos (BDR), operaciones, tareas humanas, épicas cross-repo. Ejemplos reales: promos de lanzamiento (`newhaze-workspace#90`), packs en el sheet (`#61`). Label `repo:<codebase>` si referencia código. |
| AWI harness | `GuidoAmici/awi-core` | Changes to the AWI system itself: skills, INSTRUCTIONS.md, hooks, documentation standards, agent behavior. |
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
3. AWI harness change (skill, hook, INSTRUCTIONS.md, doc standard) → `GuidoAmici/awi-core`
4. Personal → `GuidoAmici/my-awi-user`

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --repo <owner/repo> --comments`. Infer the repo from context — label, project, or codebase being worked on.

## Migration note

`agenda/tasks/` files are retired. Do not create new files there. Actionable work goes to GitHub Issues.
`agenda/projects/` files are kept — they are context/scope documents, not issue lists.
