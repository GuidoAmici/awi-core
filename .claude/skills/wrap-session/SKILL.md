---
name: wrap-session
description: End-of-session ritual. Closes open threads first, then saves observations, publishes the shared context, and reports.
allowed-tools: Read, Write, Edit, Bash, Glob, AskUserQuestion
model: sonnet
subagent_type: general-purpose
---

# /wrap-session — End of Session

Five steps, in strict order.

**Step 1 va primero por diseño.** Antes vivía último, y el orden importaba más de lo que parecía: para cuando el gate corría, la sesión ya estaba archivada y resumida, así que todo lo que aparecía ahí llegaba como un apéndice a algo que el operador ya daba por cerrado. Lo que se decide en el Step 1 cambia lo que hay que escribir en el Step 2 y lo que hay que publicar en el Step 3 — no puede ir después de ellos.

Steps 2–3 son automáticos: sin prompts, sin confirmaciones. Step 1 usa `AskUserQuestion`, no texto libre. No imprimas progreso durante los Steps 2–3 — la salida viene en el Step 4.

---

## Step 1 — Gate de hilos abiertos

**El bloque `C` de la última respuesta es la lista, no un punto de partida.** La política de [los cinco bloques](../../../_system/_agentic-workflow-integrator/INSTRUCTIONS.md) hace que cada turno mantenga los hilos abiertos de la sesión entera, así que acá no se reconstruye nada: se levanta esa lista y se le da destino a cada ítem. El barrido de la conversación pasa a ser control, no fuente.

Para cada hilo, **una llamada a `AskUserQuestion` por vez**, esperando respuesta antes de la siguiente. No vuelques una lista en markdown ni pidas texto libre.

### 1a — Destino de cada hilo de `C`

Tomá el bloque `Hilos abiertos` de la última respuesta del agente principal. Para cada ítem, preguntá con estas cuatro opciones:

| Opción | Qué significa | Qué hacés |
|---|---|---|
| **Terminarlo ahora** | Entra antes de cerrar la sesión | Resolvelo en el momento; pasa a «Completado esta sesión» en el `2d` |
| **Convertirlo en issue** | Sobrevive a la sesión con dueño y enlace | Creá el issue siguiendo [`docs/agents/issue-tracker.md`](../../../docs/agents/issue-tracker.md) y devolvé el número |
| **Dejarlo para mañana** | Queda sólo en el daily, sin issue | Va a «Hilos abiertos» del `2d` — decile al operador que si mañana no lo levanta, se pierde |
| **Abandonarlo** | No va | Confirmalo y no lo escribas en ningún lado |

**«Terminarlo ahora» va primero cuando el hilo es corto.** El bloque `C` suele decir exactamente qué falta —«faltan `billing.ts` y `webhooks.ts`, mismo patrón»—; si eso entra en la sesión, cerrarlo cuesta menos que filear un issue y volver a cargarlo mañana.

**Un hilo que se descompone en varias unidades entregables no es un issue, es una épica:** issue padre con sub-issues, en el workspace repo de la org, que es donde `issue-tracker.md` ya ubica las épicas cross-repo. Preguntalo como parte de la opción "Convertirlo en issue", no como una quinta opción.

**Si no hay bloque `C` disponible** —la sesión no usó los bloques, o esta skill corre sin la conversación— saltá a `1b` y usalo como fuente.

### 1b — Verificación: lo que `C` no registró

Recorré la sesión buscando lo que quedó a mitad de camino y no está en la lista:

- Tareas empezadas y nunca cerradas
- Issues que el trabajo de hoy resolvió, invalidó o hizo obsoletos, y que siguen abiertos sin comentario (la política está en «Issue hygiene» de INSTRUCTIONS.md — comentar y **sugerir** la disposición, no cerrar solo)
- Decisiones tomadas en la conversación que ameritan un ADR y no lo tienen
- Cambios de código sin commitear que no son contexto — el Step 3 publica los repos de contexto, no los repos de trabajo del harness

Lo que aparezca acá y no estuviera en `C` se trata igual: misma pregunta, mismas cuatro opciones.

**Si el barrido encuentra bastante que `C` no tenía, decilo en el Step 5.** Significa que el bloque no se mantuvo durante la sesión, y es lo único que puede detectarlo.

### 1c — Información sin guardar

Recorré la sesión buscando lo que se mencionó y no se archivó:

- Tareas o to-dos referidos pero nunca creados
- Ideas o decisiones que pertenecen al vault
- Cambios de estado de proyectos que todavía no están en los archivos
- Personas o reuniones nombradas al pasar

Si no hay nada abierto en ninguno de los tres barridos, decilo en una línea y pasá al Step 2.

Lo que el operador decida guardar entra en los archivos del Step 2.

---

## Step 2 — Guardar todos los archivos, en silencio

Guardá cada archivo de abajo sin pedir confirmación. No pauses entre guardados.

### 2a — Resolver contexto

```bash
bash .claude/hooks/get-datetime.sh full
gh api user --jq '{id: .id, login: .login, name: .name}'
```

Leé `_data/users/current-user.json` para obtener `<user-root>`.

### 2b — Inferir qué orgs se tocaron

Una org se tocó si se cumple alguna de estas:
1. Se editaron archivos bajo `_data/organizations/<name>/`
2. Se referenciaron issues de un repo workspace de la org (p. ej. `GuidoAmici/newhaze-workspace`, `GuidoAmici/rabbitek-workspace`)

El nombre de la org es el prefijo del repo antes de `-workspace` (p. ej. `newhaze` de `GuidoAmici/newhaze-workspace`). Armá la lista de orgs tocadas — se usa en los pasos 2d y 2e.

### 2c — Archivo de inferencias del usuario

Ruta: `<user-root>agenda/user-profile-inference/YYYY-MM-DD-<login>.md`

Revisá la conversación buscando patrones de comportamiento que el operador quizás no registra conscientemente:
- Cómo se comunica (verbosidad, estilo de delegación, confianza)
- Cómo decide (por datos, por intuición, por influencia social)
- Qué evita, qué asume, qué no nota
- Diferencias entre lo que pidió y lo que en realidad necesitaba

Escribí 1–3 observaciones. Cada una debe ser:
- **Específica de esta sesión** — anclada en lo que pasó de verdad
- **No valorativa** — planteada como observación, no como evaluación
- Sobre algo que probablemente no registra
- **Con Pros y Contras explícitos**

Antes de escribir, revisá las entradas existentes para no repetirte:
```bash
ls <user-root>agenda/user-profile-inference/ | sort -r | head -3
```

Formato:
```markdown
<details><summary><strong>Etiqueta corta</strong></summary>

Un párrafo corto. Específico, anclado en lo que pasó esta sesión.

**Pros:** Qué habilita este patrón o dónde le sirve.
**Contras:** Dónde puede generar fricción, puntos ciegos o costos.

</details>
```

- Si el archivo de hoy ya existe: agregá un `<details>` nuevo
- Si es nuevo: crealo con `# <nombre>` como H1 y `## YYYY-MM-DD` como sección

### 2d — Daily del usuario

Ruta: `<user-root>agenda/daily/YYYY-MM-DD.md`

Si no existe, crealo:
```markdown
---
type: daily
date: YYYY-MM-DD
checked-in: false
checked-out: false
---

# DayOfWeek, Month DD
```

Agregá una sección `## Session Log` con:

**Completado esta sesión** — todo lo hecho, marcado `[x]`, enlazado al archivo de tarea si existe. Incluí el trabajo no planificado.

**Agregado esta sesión** — cada tarea, decisión o idea creada. Para cada una: prioridad (`critical` / `high` / `medium` / `low`) y una marca: **[strategic]** o **[reactive]**.

**Hilos abiertos** — el destino que el Step 1 le dio a cada hilo de `C`, no sólo lo diferido. Los que se convirtieron en issue van con su número y no vuelven a esta lista; los que quedaron para mañana van sin enlace, para que el handoff los levante.

**Impulse check** — una línea: ¿la sesión fue mayormente estratégica o reactiva? Si dominó lo reactivo, decilo sin rodeos.

### 2e — Dailies de las orgs

Para cada org tocada, guardá `_data/organizations/<name>/agenda/daily/YYYY-MM-DD.md`.

Si no existe, creala con estructura mínima:
```markdown
---
type: daily
org: <name>
date: YYYY-MM-DD
---

# DayOfWeek, Month DD — <name>
```

Agregá una sección `## Session Log` que resuma el trabajo hecho para esa org.

### 2f — Outputs

Si la sesión produjo outputs (planes, diseños, decisiones, informes), guardalos en:
- `<user-root>agenda/outputs/YYYY-MM-DD-<slug>.md` para outputs personales
- `_data/organizations/<name>/agenda/outputs/YYYY-MM-DD-<slug>.md` para outputs de una org

Sólo creá archivos de output para contenido que se produjo de verdad, no para el session log en sí.

---

## Step 3 — Publicar el contexto compartido

Va después del Step 2 porque publica lo que el Step 2 acaba de escribir.

```bash
python3 .claude/skills/shared/scripts/context_sync.py status
python3 .claude/skills/shared/scripts/context_sync.py push --repo <nombre> --message "<mensaje>"
```

Un `push` por repo con cambios, **sin pedir confirmación**. Redactá vos el mensaje de cada repo en [Conventional Commits](../../../_system/_agentic-workflow-integrator/references/commit-format.md), describiendo lo que cambió de verdad — nunca un mensaje genérico repetido.

Si `status` no reporta nada, no corras `push`.

Los codebases que `status` liste en su sección aparte **no se publican acá**: el código avanza en su propia sesión, supervisado. Si tienen trabajo pendiente, eso es un hilo abierto — nombralo en el Step 5, no lo publiques.

Si un repo vuelve `conflicto`, `sensible` u `otra-rama`, **no lo resuelvas por tu cuenta**: mostralo en el Step 4 con el detalle que devolvió. El repo quedó como estaba y los demás sí se publicaron.

---

## Step 4 — Una línea por archivo guardado y por repo publicado

```
_data/users/42481462/agenda/user-profile-inference/2026-05-14-GuidoAmici.md — 2 observaciones
_data/users/42481462/agenda/daily/2026-05-14.md — session log agregado
_data/organizations/newhaze/agenda/daily/2026-05-14.md — creado, session log agregado
_data/users/42481462/agenda/outputs/2026-05-14-wrap-session-rewrite.md — creado

Publicado:
  ↑ newhaze    docs(newhaze): auditoría de identidad visual de Mark
  ↑ 42481462   docs(agenda): cierre de sesión del 14/05
```

---

## Step 5 — Resumen de la sesión

3–6 viñetas sobre acciones tomadas e hilos que quedan abiertos. Resultados, no proceso.

Si el `1b` encontró trabajo a medias que el bloque `C` no tenía, decilo acá en una línea con el número: es la señal de que los hilos no se mantuvieron durante la sesión.

```
## Session summary
- [acción o resultado]
- [acción o resultado]
- ...
```

---

## Logging

```bash
python3 .claude/skills/shared/scripts/log_command.py wrap-session <outcome>
```

`<outcome>`: `completed` | `skipped` | `errored`
