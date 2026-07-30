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

Lo que **sí** se descarta: cambios locales en archivos del harness. El script los lista antes de descartarlos, así que nada desaparece en silencio.

---

## Steps

### Step 1 — Mirar antes de tocar

```bash
python3 .claude/skills/awi-update/scripts/awi_update.py --check
```

Reporta sin modificar nada: qué versión hay y qué versión viene, los cambios agrupados por tipo, qué archivos locales se van a descartar, y si la promoción de `dev` a `main` está colgada.

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
| `1` | Error de git o de red | Leer el mensaje. Si es de red, reintentar; si es de git, escalar al operador |
| `2` | Rechazado: la instancia está en `dev` | **No forzar.** Es una instancia de desarrollo del harness y un reset borraría trabajo sin pushear |

## Si el diagnóstico avisa que la promoción está colgada

El script reporta cuántos commits de `dev` no llegaron a `main`. Puede ser normal —están esperando que pasen los tests— o puede ser que la promoción se rompió. Es diagnóstico, no un gate: si el número no baja entre sesiones, avisale al operador de que revise el CI. La promoción anterior falló en 4 de 4 corridas durante días sin que nadie lo notara, y esta línea existe para que eso no se repita.

## Qué no hace esta skill

- **No sincroniza los repos de contexto** (workspaces de org y sus codebases). Eso es otro ciclo, coordinado desde `INSTRUCTIONS.md`: pull al abrir la sesión, commit y push sugeridos al cerrar.
- **No publica nada.** No pushea, no commitea, no toca `dev`.
