---
name: break
description: Log a break to today's daily file. Tracks start/end times and motive so /wrap-session can calculate actual work time.
---

# /break - Log a Break

Logs break time to today's daily file. Used to track actual working time vs planned time.

---

## Path Resolution

Before accessing any agenda files:

1. Read `_data/users/current-user.md`
2. Extract the `user:` field — this is `<user-root>` (e.g. `_data/users/42481462/`)
3. `<agenda-base>` = `<user-root>agenda/`

If `current-user.md` does not exist: stop and tell the operator to run `/awi-user-login`.

---

## Usage

- `/break <motive>` — start a break (logs current time + reason)
- `/break back` — end a break (logs current time as break end, shows duration)

---

## How it works

Get the current time:
```bash
bash .claude/hooks/get-datetime.sh time
```

Read `<agenda-base>daily/YYYY-MM-DD.md`.

If the file doesn't exist, say:

> No daily file for today. Run `/today-start` first.

### Starting a break (`/break <motive>`)

Append to the `## Breaks` section:

```markdown
- **HH:MM** — [motive] — started
```

**Después de escribir la línea, publicá el contexto compartido.** Un descanso es el corte lógico más barato que hay: el trabajo ya está hecho y nadie lo está tocando.

```bash
python3 .claude/skills/shared/scripts/context_sync.py status
python3 .claude/skills/shared/scripts/context_sync.py push --repo <nombre> --message "<mensaje>"
```

Un `push` por repo con cambios, **sin pedir confirmación**, con un mensaje que vos redactás describiendo lo que cambió de verdad ([Conventional Commits](../../../_system/_agentic-workflow-integrator/references/commit-format.md)). Si `status` no reporta nada, no corras `push`.

Los codebases que `status` liste en su sección aparte **no se publican acá**: el código avanza en su propia sesión, supervisado. Nombralos si hay algo pendiente, y nada más.

Contale al operador qué se publicó, una línea por repo:

> Break started at HH:MM. Say `/break back` when you're back.
>
> Publicado: `newhaze` — docs(newhaze): auditoría de identidad visual de Mark

Si algún repo vuelve `conflicto` o `sensible`, decilo acá: es el mejor momento para enterarse, no al cerrar la sesión. No lo resuelvas por tu cuenta.

### Ending a break (`/break back`)

Traé lo que haya pasado mientras no estabas, sin preguntar:

```bash
python3 .claude/skills/shared/scripts/context_sync.py pull
```

Find the last `started` entry in `## Breaks` that has no end time. Calculate duration.

Update the line:

```markdown
- **HH:MM – HH:MM** — [motive] — Xm
```

Calculate running totals and tell the operator:

> Back at HH:MM. Break was Xm. Total breaks today: Xh Ym. Remaining work time: Xh Ym.

Si el `pull` trajo cambios de otra persona, nombralos en una línea antes de los totales. Si no, no lo menciones.

---

## Running totals

When ending a break, always show:

```
Break:              Xm ([motive])
Total breaks today: Xh Ym
Remaining work time: Xh Ym
```

Read the `## Time Budget` section to calculate remaining work time = available - breaks taken.

---

## Logging

At the end of this skill — regardless of outcome — log the invocation:

```bash
python3 .claude/skills/shared/scripts/log_command.py break <outcome>
```

`<outcome>`: `completed` | `skipped` | `errored`
