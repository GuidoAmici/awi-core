# AWI — Agentic Workflow Integrator

AWI es el gestor de contexto empresarial del operador: ordena en un filetree la agenda, la documentación y las decisiones de cada organización, y las deja al alcance de la sesión donde se toma la decisión. Este archivo es la fuente de verdad de sus reglas — no hay otro documento que haya que leer antes de operar.

La forma de la respuesta no vive acá: la trae el plugin [`answerable`](plugins/answerable/rules/answerable.md), que la inyecta al abrir la sesión.

## Siempre

- **La fecha se pregunta, no se supone:** `bash .claude/hooks/get-datetime.sh full`.
- **Medí el artefacto antes de citar lo que se escribió sobre él.** El `.blend`, la base, el repo son la verdad; un handoff o un output son afirmaciones sobre ella, y envejecen solas. Antes de medir, fijate si tenés el original o una copia (una exportación, un `.xlsx` bajado). Si es copia y el original no se puede leer, la fecha de la copia va en la primera línea del resultado.
- **Los comandos que ejecutás vos llevan rutas relativas** desde la raíz del proyecto. Una ruta absoluta puede pedir un permiso que la relativa ya tiene.
- **Commiteá en los cortes lógicos de la tarea**, en [Conventional Commits con scope](_system/_agentic-workflow-integrator/references/commit-format.md) — `docs(newhaze): …`, `chore(sync): …`. No hay hook de auto-commit: no dejes trabajo terminado sin commitear, ni commitees después de cada `Write`.
- **`<user-root>` se resuelve leyendo** `_data/users/current-user.json` → campo `user`. De ahí salen todas las rutas de agenda; `<agenda-base>` es `<user-root>agenda/`.
- **Las rutas de directorio se declaran en un solo lugar,** `.claude/skills/shared/scripts/paths.py`. Un script las importa de ahí; un `SKILL.md` nombra la constante (`ORGANIZATIONS_RELDIR`) en vez de escribir la ruta.

## Tocar código es pedir un worktree

Un working tree tiene un solo `HEAD`, y dos sesiones sobre el mismo checkout se pisan **en silencio**: seguís trabajando, commiteás sobre la base equivocada y te enterás cuando el PR trae los commits de otra rama. Ya pasó una vez y costó rehacer una entrega entera.

Antes de la primera rama o el primer commit en un codebase:

```bash
python3 .claude/skills/shared/scripts/worktree.py provision <codebase> <tu-rama>
```

Te da un directorio propio bajo `.claude/worktrees/`, con los archivos ignorados symlinkeados y un puerto de dev server que no choca. `worktree-guard.py` bloquea el `git checkout` que se saltee esto. Qué aísla y qué no —el stack de base de datos no— está en [`docs/agents/worktrees-paralelos.md`](docs/agents/worktrees-paralelos.md).

## Docker apagado lo levantás vos

Si necesitás Docker y falla con `failed to connect to the docker API`, no se lo pidas al operador:

```bash
bash .claude/hooks/docker-up.sh
```

Sale enseguida si ya corría, y espera al daemon y no al proceso. Sólo sale con 1 cuando hace falta el operador de verdad — login vencido, actualización pendiente—; ahí se lo decís nombrando qué falló. La trampa de la integración WSL contra interop está en [`docs/agents/docker-wsl.md`](docs/agents/docker-wsl.md).

## Contexto compartido

Traer y publicar el contexto de los repos materializados **no se pregunta**: cada momento está anclado como paso numerado de la skill que lo abre —`/today`, `/triage`, `/delegate-issue`, `/break`, `/wrap-session`— y la mecánica vive en `context_sync.py`. Alcanza a agendas y documentación, nunca a los codebases. Los estados `conflicto`, `sensible` y `otra-rama` los decide el operador: [`docs/agents/contexto-compartido.md`](docs/agents/contexto-compartido.md).

## Agent skills

### Issue tracker

GitHub Issues distribuidos por alcance — repos de codebase, repos de org workspace y `GuidoAmici/my-awi-user` para trabajo cruzado. Cuándo preferir MCP sobre `gh`, cómo se cierra el loop de un issue resuelto y qué issue está en juego contra qué duerme: `docs/agents/issue-tracker.md`.

### Triage labels

Vocabulario por defecto: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Multi-context layout — `CONTEXT-MAP.md` at root points to per-org `CONTEXT.md` files under `_data/organizations/`. See `docs/agents/domain.md`.

### Pentesting con IA

Strix — agente open-source de pentesting con IA (corre la app, exploita fallas y adjunta un PoC a cada hallazgo). Adoptado en dos capas: guardarraíl por PR-diff en CI y auditoría completa a demanda. Los hallazgos entran al issue tracker vía triage. See `docs/agents/strix-pentesting.md`.

### Artifacts

Todo artifact se compone con el **Design System de la org destinataria** —se resuelve antes de escribir la primera línea de HTML, no al final—, el fuente HTML/MD se versiona en el repo (nunca en el scratchpad) y la trazabilidad artifact ↔ repo es bidireccional. See `docs/agents/artifacts.md`.

### Delegar a un subagente

La persona-agente aporta el rol; **el brief aporta el stack**, porque el roster viene de un upstream ajeno escrito contra otro stack. Nunca se editan las personas localmente. `docs/agents/delegacion.md`.

### Registrar una decisión

Toda decisión de arquitectura o cambio de convención va como output en `<user-root>agenda/outputs/`, y un ADR lleva `status:` en su frontmatter. El campo `affects:` conecta el output con el wiki que actualiza. `docs/agents/decisiones.md`.

## Estructura

Cada `_data/organizations/<name>/` y cada `_data/users/<github-id>/` es **un repo de git aparte**, declarado en `user-submodules.json` y materializado por `git clone`. Nada en AWI es un submódulo — ver [ADR 0009](docs/adr/0009-manifiestos-json-en-lugar-de-submodulos.md). `_data/` está en `.gitignore` por corrección, no por higiene: sin eso un `git add -A` en la raíz se traga los hijos como repos embebidos.

`/awi-org <name>` scaffoldea una organización nueva y la registra.

## Referencia

| Cuándo | Dónde |
|---|---|
| Definir un término del dominio | [definitions.md](_system/_agentic-workflow-integrator/definitions.md) y [CONTEXT.md](CONTEXT.md) |
| Escribir un archivo de agenda | [file-formats.md](_system/chief-of-staff/references/examples/file-formats.md) |
| Decidir si algo va a `people/` o a `user-profile-inference/` | [routing-rules.md](_system/_agentic-workflow-integrator/routing-rules.md) |
| Clasificar con confianza dudosa | [confidence-scoring.md](_system/_agentic-workflow-integrator/confidence-scoring.md) |
| Escribir `.abstract.md` / `.overview.md` | [navigation-patterns.md](_system/_agentic-workflow-integrator/navigation-patterns.md) |
| Auditar qué pasó con git | [git-audit-commands.md](_system/_agentic-workflow-integrator/references/git-audit-commands.md) |
| Escribir copy para un consumidor | [tldr.md](_system/_agentic-workflow-integrator/references/tldr.md) |
| Buscar el comando de una skill | [tables/skills.md](_system/_agentic-workflow-integrator/tables/skills.md) |

## Cierre de sesión

Corré `/wrap-session`. Cierra los hilos abiertos, guarda las observaciones sobre el operador en `<user-root>agenda/user-profile-inference/`, publica el contexto compartido y reporta.
