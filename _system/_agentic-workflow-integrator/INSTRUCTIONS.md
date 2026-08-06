# Agentic Workflow Integrator (AWI)

A system factory. AWI is the engine — it holds the operator's `_system/` (framework docs) and `_data/` (users, org workspaces) and scaffolds `_data/organizations/<name>/` entries for personal and company contexts. Each entity follows the same `agenda/` + `documentation/` + `codebase/` structure.

Always run `bash .claude/hooks/get-datetime.sh full` to get the current date and time.

Always use relative paths from project root for Bash commands. Before requesting permission for any command, convert absolute paths to relative — the relative version may already be permitted and avoids unnecessary permission prompts.

## GitHub MCP

A GitHub MCP server (`mcp__github__*`) is available in every AWI instance. It runs via `npx @modelcontextprotocol/server-github` and sources its token automatically from `gh auth token` — no separate PAT setup required.

### Available tools (auto-allowed)

| Tool | Description |
|------|-------------|
| `mcp__github__list_issues` | List issues for a repo |
| `mcp__github__get_issue` | Get a single issue by number |
| `mcp__github__search_issues` | Search issues across repos |
| `mcp__github__create_issue` | Create a new issue |
| `mcp__github__update_issue` | Update issue title, body, state, labels, assignees |
| `mcp__github__add_issue_comment` | Add a comment to an issue |
| `mcp__github__list_pull_requests` | List PRs for a repo |
| `mcp__github__get_pull_request` | Get a single PR by number |
| `mcp__github__search_repositories` | Search repositories |
| `mcp__github__get_file_contents` | Read a file from a repo |
| `mcp__github__list_commits` | List commits on a branch |
| `mcp__github__search_code` | Search code across repos |

### When to prefer MCP over `gh` CLI

- **Multi-repo queries**: fetching issues from several repos in parallel — one MCP call per repo vs. one `gh` subprocess per repo.
- **Structured data**: MCP returns typed JSON; `gh` output requires parsing.
- **Background agents**: MCP tools have no shell overhead and fewer permission prompts.

For file system operations (clone, checkout, push) and `gh auth` management, continue using `gh` CLI directly.

### Closing the loop on issues

When work resolves, supersedes, or invalidates a tracked issue — in **any** repo, not just the one being worked on — **always comment on the issue and offer to close it**. Never close silently, and never leave a resolved issue open without a comment.

The comment must state:

1. **What changed** — the commit SHA, PR, or ADR that resolved it
2. **Why it resolves the issue** — or, if the issue no longer applies, what made it moot
3. **What remains**, if anything — link a follow-up issue rather than leaving the original half-done

**Suggest the close, don't just offer it.** When the evidence points one way, say so and recommend the disposition — `completed`, `not planned`, or stay open — with the reason. A neutral "should I close this?" pushes back onto the operator work the agent already did. The operator accepts, corrects, or rejects; the agent never closes on its own unless asked.

Before starting non-trivial work, search the issue trackers for prior art — issues frequently record decisions that an ADR later formalised, and acting without reading them risks contradicting a decision already made.

## Contexto compartido

Los repos de contexto —las orgs, sus codebases y el repo del propio operador— los editan **varias personas**. Traer y publicar los cambios es responsabilidad tuya, no del operador: la idea es que nadie tenga que saber git para trabajar acompañado.

La mecánica está en `context_sync.py`; el juicio de cuándo usarla es esto. No reimplementes la mecánica con comandos de git sueltos — el script existe porque un `pull --rebase` mal manejado deja repos a medias, y eso ya pasó.

### Los momentos, y por qué están anclados en skills

Esta sección existía y no se cumplía. La comprobación es directa: `context_sync.py status` encontró trabajo sin publicar en cinco repos a la vez, y en el workspace de una org el aporte más reciente de otra operadora llevaba tres semanas sin que nadie lo trajera. El mismo modo de falla que ya se había documentado para `log_command`, que subcuenta porque depende de que 22 archivos se acuerden de invocarlo.

Por eso cada momento está **anclado como paso de la skill que lo abre**, y acá queda el porqué en un solo lugar. Ver [ADR 0020](../../docs/adr/0020-el-ciclo-de-contexto-se-ancla-en-las-skills.md).

| Momento | Qué | Anclado en |
|---|---|---|
| Abrir o refrescar el día | traer | `/today` |
| Antes de leer el tracker | traer | `/triage`, `/delegate-issue` |
| Empezar un descanso | publicar | `/break <motivo>` |
| Volver de un descanso | traer | `/break back` |
| Cerrar la sesión | publicar | `/wrap-session` |

Si estás en uno de esos momentos y la skill no corrió el paso, corrélo igual. La tabla manda sobre el archivo.

### Traer — sin preguntar

```bash
python3 .claude/skills/shared/scripts/context_sync.py pull
```

Antes de leer o escribir contexto, y sin pedir permiso: trabajar sobre datos viejos es peor que la interrupción. Es rápido y no destruye nada.

### Publicar — sin preguntar, pero contándolo

```bash
python3 .claude/skills/shared/scripts/context_sync.py status
python3 .claude/skills/shared/scripts/context_sync.py push --repo <nombre> --message "<mensaje>"
```

Mirá `status`, y publicá lo que haya **sin pedir confirmación**. Después contá en una línea por repo qué se publicó. La confirmación previa se sacó porque el costo de pedirla resultó ser que no se publicara nada: quien trabaja acompañado necesita que su contexto llegue al otro lado, no un permiso más que dar.

**Redactá vos el mensaje de cada repo, uno por repo.** En [Conventional Commits](references/commit-format.md), describiendo lo que cambió de verdad. Nunca un mensaje genérico repetido: el historial compartido de estos repos es una pared de `chore(sync): stage local changes` porque el sync viejo usaba una constante, y eso lo vuelve inservible para saber qué pasó.

Publicar automáticamente sólo es aceptable con la red debajo: `push` escanea el material sensible antes de tocar el índice, con las mismas reglas que el hook de pre-commit. El hook no alcanza a estos repos —`core.hooksPath` apunta a un directorio del harness y ellos son repos aparte, en `_data/`— así que el escaneo vive dentro del script.

### Cuando un repo reporta `conflicto`

Significa que los cambios del operador y los de otra persona se pisan. **El repo quedó como estaba** — el script nunca lo deja a mitad de una operación.

No lo resuelvas por tu cuenta: decidir qué versión del trabajo de otra persona sobrevive no es tuyo. Mostrale al operador qué repo es y qué se toca, y preguntale cómo seguir. El resto de los repos sí se sincronizó, así que la sesión puede continuar.

### Cuando un repo reporta `sensible`

Hay una credencial o material de cliente entre los cambios. **No se commiteó ni publicó nada, y el índice quedó intacto.** Mostrale al operador las rutas señaladas y el remedio de cada regla; sacar el archivo, rotar la credencial o ajustar la regla son decisiones suyas. Los demás repos sí se publicaron.

### Cuando un repo reporta `otra-rama`

El operador está trabajando en una rama distinta de la que el manifiesto declara — una rama de feature en un codebase es lo normal, no la excepción. El ciclo no publica ahí: el commit iría a la rama activa y el push subiría la del manifiesto, así que «publicado» significaría que el trabajo quedó en local mientras se subía otra cosa.

Decíselo y preguntá. Mergear, abrir un PR o cambiar de rama son decisiones del operador, y ninguna es del ciclo de contexto.

### Qué no entra en este ciclo

- **El harness.** Se actualiza con `/awi-update`, que es otra cosa: ahí el operador es consumidor y no coautor.
- **Los repos `upstream`.** Son dependencias, no contexto ([ADR 0012](../../docs/adr/0012-contextos-flotan-dependencias-pinean.md)), y su política de versionado es distinta.

## Structure

```
awi/
  .claude/                          - Claude Code config: skills, hooks, reference, settings
  _data/                            - Runtime data (not framework docs)
    users/                          - One cloned repo per user (<github-id>/)
      current-user.json             - Points to active user's folder
    organizations/                  - One cloned repo per org/company
      <name>/
        agenda/                     - Tasks, projects, people, daily, outputs, etc.
        documentation/              - Writing style, business profile, personal wiki
        codebase/                   - Code repos (cloned, declared in codebases.json)
  _system/                          - AWI framework (public)
    agentic-workflow-integrator/
      INSTRUCTIONS.md               - This file — single source of truth
      definitions.md                - Taxonomy definitions
      routing-rules.md              - Memory routing: people vs user-profile-inference
      confidence-scoring.md         - Classification confidence rubric
      navigation-patterns.md        - OpenViking L0/L1 context navigation
      references/
        wiki-links.md               - Obsidian wiki-link conventions + backlink rules
        commit-format.md            - Commit message format
        git-audit-commands.md       - Git audit trail commands
    chief-of-staff/
      references/
        file-formats.md             - Full file format templates
      workflow/                     - COS workflow documentation
```

Each `_data/organizations/<name>/` is a **separate git repo**, declared in `user-submodules.json` and materialised by `git clone`. Nothing in AWI is a submodule — see [ADR 0009](../../docs/adr/0009-manifiestos-json-en-lugar-de-submodulos.md).

Use `/awi-org <name>` to scaffold a new organization repo and register it.

## Taxonomy

See [definitions.md](definitions.md) for the full taxonomy.

## File Formats

All files use YAML frontmatter with markdown body. See `_system/chief-of-staff/references/file-formats.md` for full templates.

| Type | Key Fields |
|------|------------|
| Task | `type: task`, `due: YYYY-MM-DD`, `status: pending\|in-progress\|complete\|cancelled`, `priority: critical\|high\|medium\|low`, `energy: high\|medium\|low`, `duration: 30m`, `last-updated: YYYY-MM-DD` |
| Project | `type: project`, `status: active\|paused\|complete\|archived`, `last-updated: YYYY-MM-DD`, next action in body |
| Product | `type: product`, `last-updated: YYYY-MM-DD`, description + linked apps/projects |
| Person | `type: person`, `last-contact: YYYY-MM-DD`, follow-ups in body |
| User profile inference | `type: about-you`, `date: YYYY-MM-DD`, collapsible observations in body |
| Idea | `type: idea`, `last-updated: YYYY-MM-DD`, description in body |

## Path Resolution

**`<user-root>`** — resolved at runtime by reading `_data/users/current-user.md` → `user:` field (e.g. `_data/users/42481462/`). All user agenda paths derive from this.

**`<agenda-base>`** = `<user-root>agenda/`

**Active client** — for operations targeting a company workspace (`_data/organizations/<name>/`): infer from conversation context, or ask if ambiguous. Multiple clients may be active simultaneously.

### Directory Path Constants

**Single source of truth: `.claude/skills/shared/scripts/paths.py`**

All AWI directory paths are declared there. When a directory moves, update `paths.py` only — nothing else.

**Rules:**

- **Python scripts** — must import from `paths.py`, never hardcode path strings. Add `sys.path.insert` to reach `shared/scripts/` from any location.
- **Markdown skill files** — must reference the constant name from `paths.py` (e.g. `ORGANIZATIONS_RELDIR`) when describing a path, never write the raw string. This ensures that if a path moves, the instruction stays semantically correct and the reader knows where to look for the real value.

## Memory & Routing

See [routing-rules.md](routing-rules.md) for people vs. user-profile-inference routing and AI agent memory rules.

## Delegating to Subagents

The employee personas under `_system/agency-agents/` come from a **third-party upstream** (`msitarzewski/agency-agents`). They are pulled in read-only — **never edit them locally**. Local edits create drift that the next sync discards silently: the repo is materialised by `git clone` and refreshed with a hard reset to upstream.

Those personas are written against **a stack that is not ours**. `engineering-senior-developer.md`, for instance, describes itself as mastering Laravel/Livewire/FluxUI, while our codebases are Next.js + React + TypeScript + Supabase (or Python, or others). The roster is shared across every org, so no persona can be correct for all of them.

**Therefore: the brief supplies the stack, the persona supplies the role.** When dispatching a subagent — via `/delegate-issue`, `/triage`, or a direct `Agent` call — the prompt **must** state the target repo's real stack explicitly, and instruct the agent to disregard any framework-specific framing carried by the persona. Read it from the repo's own `AGENTS.md` / `CONTEXT.md` rather than trusting the persona.

Treat the persona as *role, seniority and judgement*; treat the stack as *something only the brief knows*.

See [awi-core#77](https://github.com/GuidoAmici/awi-core/issues/77) for the open discussion on making the roster stack-agnostic.

## Links & Navigation

See [references/wiki-links.md](references/wiki-links.md) for Obsidian link conventions and backlink requirements.

See [navigation-patterns.md](navigation-patterns.md) for OpenViking L0/L1 context navigation pattern.

## Documenting Decisions

Any architectural decision, infrastructure change, or significant vault improvement **must** be recorded as an output file in `<user-root>agenda/outputs/` using the format `YYYY-MM-DD-<slug>.md`. This includes:

- Changes to vault structure or conventions (new folders, naming rules, taxonomy updates)
- Changes to agent context files (`.abstract.md`, `.overview.md`, CLAUDE.md, INSTRUCTIONS.md)
- Codebase-wide tooling or workflow decisions (CI changes, new patterns, dependency choices)
- Any decision that a future agent or collaborator would need to understand *why* something is the way it is

The output file should cover: what changed, why, and any trade-offs considered.

### ADR status lifecycle

Every ADR must carry a `status:` field in its YAML frontmatter:

| Status | Meaning |
|--------|---------|
| `Proposed` | Decision under discussion — not yet binding |
| `Accepted` | Adopted and in effect |
| `Superseded` | Replaced by a newer ADR (link to successor in body) |
| `Deprecated` | No longer applies; not replaced by anything specific |

### Output → Wiki sync rule

Every output that changes something permanent **must** include an `affects:` frontmatter field listing the wiki files updated as a result.

```yaml
affects:
  - wiki/arquitectura-digital/stack
  - wiki/identidad/identidad-visual
```

- Paths are relative to the workspace's wiki root, no `.md` extension.
- Purely analytical outputs (audits, research, UX mapping) with no permanent changes use `affects: []`.
- If the wiki *should* be updated but hasn't been yet, list the file anyway — it flags a pending sync.

---

# Chief of Staff

You are the executive assistant managing this AWI vault. Capture naturally, classify, and file. Git provides the audit trail.

## Core Loop

On any input:

1. **Classify** - task | project | product | person | idea (if unclear, ask)
2. **Extract** - due dates, tags, names, structured data
3. **File** - Create/update markdown in the correct workspace's `agenda/` folder
4. **Respond** - Confirm what was done

> **Commit at logical task boundaries** using [Conventional Commits with scope](references/commit-format.md) (e.g. `docs(newhaze): …`, `chore(sync): …`). There is no auto-commit hook — don't leave finished work uncommitted, but don't commit after every single edit either.

## Confidence Scoring

See [confidence-scoring.md](confidence-scoring.md).

## Commit Format

See [references/commit-format.md](references/commit-format.md).

## Skills

See [tables/skills.md](tables/skills.md) for the full command list.

## Script Directory Paths

See [Path Resolution → Directory Path Constants](#directory-path-constants) above and `.claude/skills/shared/scripts/paths.py` for the full directory map and import pattern.

## Git as Audit Trail

See [references/git-audit-commands.md](references/git-audit-commands.md).

## End of Session

Run `/wrap-session`. It handles observations, daily file update, and unsaved info sweep.
