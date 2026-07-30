# Delegation

Delegate work to specialized AI employees running in separate terminal sessions.

---

## Qué es una persona-agente

Una definición de agente con nombre, descubierta desde `_system/agency-agents/`.
El archivo del agente es su prompt de sistema, su directorio es su categoría, y
el `description` de su frontmatter es el tagline con el que se rutea.

No hay registro que configurar: agregar una persona-agente es agregar un archivo.

```bash
# todas, o filtradas por nombre, categoría o tagline
python3 .claude/skills/shared/scripts/agent_personas.py [término]

# sólo las categorías, con cuántas tiene cada una
python3 .claude/skills/shared/scripts/agent_personas.py --categorias

# la ruta de una, o un error que nombra las parecidas
python3 .claude/skills/shared/scripts/agent_personas.py --resolver backend-architect
```

El registro escrito a mano que esto reemplaza tenía 36 entradas, y dos estaban
rotas: una apuntaba a un archivo inexistente y otra listaba un playbook como si
fuera un agente. Un registro a mano sobre un árbol de 292 archivos que un tercero
puede cambiar sin aviso está desactualizado por construcción. Ver
[ADR 0008](../../../../docs/adr/0008-agent-discovery-desde-agency-agents.md).

---

## Delegate Work

```bash
/delegate gemini-website: update the header component colors to match new token file
```

A separate Claude instance spawns in a new terminal, working in the employee's repo. When done:
- Task file updates with output locations
- Notification sound plays
- Full traceability via git log

---

## Gemini Delegation — Frontend Changes

Frontend file changes are **always delegated to Gemini CLI employees**:
- Claude handles: architecture, tokens, API schemas, decisions
- Gemini handles: CSS edits, font changes, component mechanical edits

---

## How It Works

1. Builds the prompt with full context (absolute paths, source repo reference)
2. Launches it with `delegate_run.py`, which spawns a detached background worker:
   ```bash
   python3 .claude/skills/delegate-issue/scripts/delegate_run.py \
     --prompt "<prompt>" --model opus --effort high [--repo <path>] [--timeout 2700]
   ```
3. The worker runs `claude -p` with `CLAUDE_DELEGATED=1`, streaming into
   `.claude/tmp/delegates/<slug>/output.log` and tracking `status.json`
4. **A wall-clock cap applies** — 45 min by default, `--timeout` to change it. On
   expiry the delegate gets SIGTERM (so it flushes its log), then SIGKILL if it
   does not exit within 30s, and lands as `timed-out`. Without the cap a stuck
   delegate ran indefinitely, billing tokens with nothing watching
5. On exit it appends a line to `.claude/tmp/delegates/inbox.md`, which the
   `UserPromptSubmit` hook surfaces on your next message, and plays a beep

Monitor with `delegate_monitor.py <slug>`, stop one with `delegate_kill.py <slug>`.

---

## Model Selection

| Variable | Model | Use Case |
|----------|-------|----------|
| `DEFAULT_MODEL` | opus | Standard delegation |
| `HEAVY_MODEL` | opus | Complex multi-step work |
| `BASE_MODEL` | sonnet | Moderate complexity |
| `FAST_MODEL` | haiku | Quick operations |
