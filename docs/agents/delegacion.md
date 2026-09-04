# Delegating to Subagents

The employee personas under `_system/agency-agents/` come from a **third-party upstream** (`msitarzewski/agency-agents`). They are pulled in read-only — **never edit them locally**. Local edits create drift that the next sync discards silently: the repo is materialised by `git clone` and refreshed with a hard reset to upstream.

Those personas are written against **a stack that is not ours**. `engineering-senior-developer.md`, for instance, describes itself as mastering Laravel/Livewire/FluxUI, while our codebases are Next.js + React + TypeScript + Supabase (or Python, or others). The roster is shared across every org, so no persona can be correct for all of them.

**Therefore: the brief supplies the stack, the persona supplies the role.** When dispatching a subagent — via `/delegate-issue`, `/triage`, or a direct `Agent` call — the prompt **must** state the target repo's real stack explicitly, and instruct the agent to disregard any framework-specific framing carried by the persona. Read it from the repo's own `AGENTS.md` / `CONTEXT.md` rather than trusting the persona.

Treat the persona as *role, seniority and judgement*; treat the stack as *something only the brief knows*.

**El informe final vuelve en los cinco bloques con dirección, y cada ítem con su TLDR en negrita** — ver [`answerable`](../../plugins/answerable/rules/answerable.md). El brief pide las dos cosas explícitamente, porque el subagente lee esta sección y no aquella. Un informe donde los ítems anuncian en vez de afirmar obliga a leerlo entero para saber qué encontró. Un informe sin direcciones obliga al agente principal a reescribirlo entero antes de pasarle nada al operador, y ahí es donde se pierde lo que el subagente encontró. El brief que se le manda, en cambio, es un documento: abre con TLDR.

See [awi-core#77](https://github.com/GuidoAmici/awi-core/issues/77) for the open discussion on making the roster stack-agnostic.
