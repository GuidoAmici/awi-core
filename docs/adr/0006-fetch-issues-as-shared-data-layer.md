# fetch_issues.py como capa de datos compartida para issue fetching

Las skills que necesitaban issues de GitHub (`/today`, `/delegate-issue`) llamaban `gh issue list` directamente desde sus SKILL.md, disparando N prompts de permisos de Bash — uno por org activa por ejecución. Además, `active-orgs.json` mantenía un registro duplicado de los repos de cada org con fines de fetching, mientras que `user-submodules.json` ya era la fuente de verdad para el resto del sistema. El resultado era dos archivos de configuración describiendo lo mismo desde ángulos distintos, y lógica de filtrado de "cross-org issues" (issues del user repo etiquetados con `org:`) que añadía complejidad sin beneficio real — ese concepto fue eliminado.

Decidimos centralizar todo el fetching de issues en un único script Python (`fetch_issues.py`) en la capa shared, importable como módulo y ejecutable como CLI. El script lee únicamente `user-submodules.json`, que recibe un campo `"type"` explícito (`"org-workspace"` | `"system-repo"`) para distinguir entradas sin depender de inferencias por prefijo de path. `active-orgs.json` se elimina; `today_issues.py` se refactoriza para importar `fetch_issues.py` directamente. `/today` agrega al check-in matutino la selección de orgs e inclusión de issues personales, persistida en el frontmatter del daily file bajo `working-orgs` e `include-personal`.

## Opciones consideradas

- **Inferencia por path prefix** (`_data/organizations/` → org workspace): descartada porque acopla la lógica de negocio a una convención estructural implícita que podría cambiar.
- **Import de módulo vs. subprocess entre scripts**: elegido import directo — mismo intérprete, mismo directorio, sin serialización JSON innecesaria. El script sigue siendo ejecutable como CLI para llamadas externas desde SKILL.md.
- **Selección de orgs por sesión vs. por consulta**: elegida persistencia en daily file (una vez por día en check-in) — coherente con el modelo existente de `energy-ceiling`, `start-time` y `end-time`.

## Consecuencias

- `active-orgs.json` queda eliminado; cualquier referencia restante en scripts o SKILL.md es un bug.
- El concepto "cross-org issue" no existe en AWI — el user repo contiene únicamente issues personales.
- `/awi-org-toggle` y `toggle_org.py` (que escribían en `active-orgs.json`) se eliminan como parte de esta migración.
