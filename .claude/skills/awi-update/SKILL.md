---
name: awi-update
description: Traer la última versión del harness de AWI a esta instancia. Para instancias consumidoras — no requiere saber git. Usage: /awi-update
---

# /awi-update — Actualizar el harness

Trae a esta instancia la última versión del harness publicada en `main`, y le cuenta al operador qué cambió en castellano en lugar de un `git log`.

Existe porque antes no había ninguna forma de que la instancia de un compañero recibiera un cambio: `pull_from_awi_core()` fue eliminado razonando desde el caso de un solo operador, y la rama por defecto sólo avanzaba al mergear a mano un PR de release. Los parches había que ir a aplicarlos a mano en cada máquina. Ver [ADR 0014](../../../docs/adr/0014-el-problema-era-la-distribucion-no-la-composicion.md).

## Usage

```
/awi-update
```

## El modelo, en una línea

**El harness lo mantiene awi-core; esta instancia lo consume.** Actualizar es un reset duro a `origin/main`, no un merge — por eso nunca hay un conflicto que resolver. Los compañeros son consumidores del harness, no coautores.

Lo que **nunca** se toca: todo `_data/` — perfiles de usuario, workspaces de org y los repos clonados adentro. Está en `.gitignore`, así que el reset no lo alcanza.

**Nada se destruye, ni siquiera en el reset.** El harness termina idéntico a lo publicado, pero el trabajo local no se paga con eso: se rescata antes de tocar el árbol.

| Trabajo local | Va a | Se recupera con |
|---|---|---|
| Commits que no están arriba | rama `respaldo/<rama>-<fecha>` | `git branch --list 'respaldo/*'` |
| Cambios sin commitear, incluidos archivos nuevos | stash `awi-update <fecha>` | `git stash list` |

Si un rescate falla, la skill aborta sin tocar nada: perder trabajo en silencio es peor que no actualizar.

Esto importa sobre todo en máquinas que estuvieron meses sin actualizarse, donde es probable que haya algo local que nadie recuerda. Y cubre el caso que el historial no puede descartar: de 1949 commits en awi-core ninguno es de un colaborador, pero el historial sólo ve lo commiteado — una edición local sin commitear es invisible ahí.

## La rama decide la operación, no sólo el ref

| Estás en | Operación | Destructivo |
|---|---|---|
| `main` (distribución) | `reset --hard origin/main` | Sí, por diseño — con el trabajo local ya rescatado |
| Cualquier otra | `merge --ff-only origin/<rama>` | **No, por construcción** |

En `main` el reset corre aunque trabajes ahí, como el mantenedor: sus commits sin pushear van a `respaldo/` y hay que recuperarlos desde esa rama. En cualquier otra rama, una que se quedó afuera obtiene una operación segura en lugar de un merge con conflictos — que es justo lo que esta skill existe para que nadie vea.

---

## Steps

### Step 1 — Mirar antes de tocar

```bash
python3 .claude/skills/awi-update/scripts/awi_update.py --check
```

Reporta sin modificar nada: qué versión hay y qué versión viene, los cambios agrupados por tipo y qué archivos locales se van a rescatar.

**Mostrale al operador ese reporte y esperá.** No apliques la actualización sin que la haya visto, salvo que la haya pedido explícitamente sin revisión.

### Step 2 — Aplicar

```bash
python3 .claude/skills/awi-update/scripts/awi_update.py
```

### Step 3 — Registrar

```bash
python3 .claude/skills/shared/scripts/log_command.py awi-update completed
```

---

## Cómo leer los códigos de salida

| Código | Qué pasó | Qué hacer |
|---|---|---|
| `0` | Actualizado, o ya estaba al día | Seguir |
| `1` | No se pudo: remoto inalcanzable, rama divergida o árbol sucio | Nada se tocó. Si es de red, reintentar. Si la rama divergió, mostrale el mensaje al operador — traerla requeriría decidir qué versión gana, y esa decisión no es de esta skill |

## Qué no hace esta skill

- **No sincroniza los repos de contexto** (workspaces de org y sus codebases). Eso es otro ciclo, coordinado desde `docs/agents/contexto-compartido.md`: pull al abrir la sesión, commit y push sugeridos al cerrar.
- **No publica nada.** No pushea ni commitea.
