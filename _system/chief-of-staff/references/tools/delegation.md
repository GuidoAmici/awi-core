# Delegation

Handing work with the scope of one issue to a **delegate**: an agent process that
runs unattended, with a wall clock cap.

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

## Con qué arranca un delegado

Un delegado **no** hereda la configuración del operador. Arranca con un perfil de
ejecución declarado en `.claude/delegate-profiles/profiles.json`, que dice qué
servidores MCP alcanza, qué flags recibe y cuál es su tope de reloj.

```bash
# los perfiles y a qué llega cada uno
python3 .claude/skills/shared/scripts/delegate_profile.py

# uno solo, con sus argumentos resueltos
python3 .claude/skills/shared/scripts/delegate_profile.py minimo
```

| Perfil | Alcanza | Para qué |
|---|---|---|
| `minimo` (por defecto) | `github` | la enorme mayoría: leer un brief, trabajar en el árbol, reportar en el issue |
| `con-base` | `github`, `supabase` | una tarea que necesita consultar la base; elegirlo es decisión del operador |
| `solo-lectura` | nada | análisis que sólo lee el árbol y produce un informe |

**El perfil por defecto es el más restrictivo**: un despacho que no elige obtiene
el mínimo, y ampliar acceso es un acto explícito que queda registrado en
`status.json`.

Lo que esto corta: antes un delegado heredaba los doce servidores del operador
—doppler (secretos), supabase (producción), mercadopago (pagos), gmail (envío de
correo) entre ellos— y corría desatendido con `--dangerously-skip-permissions`,
que además anula la única regla `deny` que el sistema declara.

**Se conserva la ejecución desatendida.** Quitar ese flag cuelga al delegado en el
primer prompt de permisos, porque no hay nadie para aprobarlo, y un delegado que
no corre desatendido no sirve de nada. Lo que cambia es lo que el flag habilita:
saltear permisos sobre un servidor de issues es defendible, saltearlos sobre doce
con credenciales de producción no.

La pieza que lo hace efectivo es `--strict-mcp-config`. Sin él, la configuración
que se pasa se **suma** a la del operador, y pasar una mínima no quitaría nada.

---

## El brief es contenido externo

El Agent Brief es un comentario en un issue de GitHub: cualquiera con permiso de
escritura en el tracker puede editar el texto que el delegado va a ejecutar.

Entra encerrado y marcado como **datos a procesar**, no como instrucciones a
obedecer, y las coincidencias con forma de directiva quedan registradas en
`status.json` — se registran, no se filtran, porque bloquear por patrón produciría
falsos positivos sobre briefs legítimos que hablan de prompts.

Esto no es una garantía: un modelo puede ignorar una delimitación. La defensa real
es el perfil, que hace chico lo que el delegado puede hacer.

---

## Trazabilidad

Cada delegado lleva un `trace_id` derivado de su issue de origen —`awi-42-a3f1c8`—
que se propaga a `status.json`, a las líneas de `inbox.md`, y a un trailer en los
mensajes de commit que el delegado produce.

```bash
# qué commits salieron de un issue
git log --grep="AWI-Trace: awi-42-" --oneline
```

Es la señal que antes no existía: «qué hizo este delegado» y «de dónde salió esto»
no tenían respuesta en ninguna parte.

---

## Cuando no puede

Antes, un `exit != 0` producía una línea en `inbox.md` y nada más. Ahora hay una
cadena, y el principio es que el sistema **siempre produce algo**:

| Cómo terminó | Qué pasa |
|---|---|
| completó y su informe cumple el esquema | se acepta |
| completó pero el informe no cumple | **degrada** — corrió y produjo algo que no era lo pedido |
| se pasó del tope, o lo mataron | **reintenta** una vez; si vuelve a pasar, escala |
| falló con exit ≠ 0 | **escala** — corrió y decidió que no podía; reintentarlo idéntico llegaría al mismo lugar |

Al degradar o escalar se escribe `escalado-<trace_id>.json` con el motivo y el
final del log. Cumple el mismo esquema que un informe exitoso, así que el
consumidor no necesita dos caminos de lectura.

Una respuesta degradada estructurada es mejor que un fallo mudo, porque un fallo
mudo se descubre tres días después.

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
