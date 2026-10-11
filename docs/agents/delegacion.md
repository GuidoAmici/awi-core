# Delegating to Subagents

## Quién hace qué ([ADR 0024](../adr/0024-delegacion-en-dos-niveles-y-preguntas-con-numero-fijo.md))

**Dos niveles:** el Chief of Staff (Opus) despacha y un [`trabajador`](../../.claude/agents/trabajador.md) (Sonnet, razonamiento medio) hace una tarea y termina. Las búsquedas masivas van a `Explore` con `model: haiku`. Los PRs con migraciones, permisos o seguridad los revisa el [`revisor`](../../.claude/agents/revisor.md) (Opus). Un trabajador no despacha trabajadores.

**El brief del trabajador trae, en este orden:**

1. **Qué tiene que quedar hecho**, en una línea: «PR contra `stg` que …».
2. **Repo, rama base y stack**, leídos del `AGENTS.md` del repo.
3. **El issue y las decisiones del operador que aplican**, citadas como «confirmado por Guido el <fecha>».
4. **Los archivos o símbolos donde empezar.** Ahorra la exploración que más contexto gasta.
5. **Qué lo frena:** las decisiones que no puede tomar solo, y las migraciones que no son expand-only.

**El informe vuelve en diez líneas como máximo.** Las preguntas para el operador vienen sin numerar, y las numera el Chief of Staff al juntarlas.

## Personas del roster

The employee personas under `_system/agency-agents/` come from a **third-party upstream** (`msitarzewski/agency-agents`). They are pulled in read-only — **never edit them locally**. Local edits create drift that the next sync discards silently: the repo is materialised by `git clone` and refreshed with a hard reset to upstream.

Those personas are written against **a stack that is not ours**. `engineering-senior-developer.md`, for instance, describes itself as mastering Laravel/Livewire/FluxUI, while our codebases are Next.js + React + TypeScript + Supabase (or Python, or others). The roster is shared across every org, so no persona can be correct for all of them.

**Therefore: the brief supplies the stack, the persona supplies the role.** When dispatching a subagent — via `/delegate-issue`, `/triage`, or a direct `Agent` call — the prompt **must** state the target repo's real stack explicitly, and instruct the agent to disregard any framework-specific framing carried by the persona. Read it from the repo's own `AGENTS.md` / `CONTEXT.md` rather than trusting the persona.

Treat the persona as *role, seniority and judgement*; treat the stack as *something only the brief knows*.

**El informe final vuelve en los cinco bloques con dirección, y cada ítem con su TLDR en negrita** — ver [`answerable`](../../plugins/answerable/rules/answerable.md). El brief pide las dos cosas explícitamente, porque el subagente lee esta sección y no aquella. Un informe donde los ítems anuncian en vez de afirmar obliga a leerlo entero para saber qué encontró. Un informe sin direcciones obliga al agente principal a reescribirlo entero antes de pasarle nada al operador, y ahí es donde se pierde lo que el subagente encontró. El brief que se le manda, en cambio, es un documento: abre con TLDR.

See [awi-core#77](https://github.com/GuidoAmici/awi-core/issues/77) for the open discussion on making the roster stack-agnostic.
