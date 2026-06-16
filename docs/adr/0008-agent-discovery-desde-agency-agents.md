# Descubrimiento de agentes desde _system/agency-agents/ en lugar de employees.json

`employees.json` era un registry manual que listaba qué agentes eran dispatchables, con su path y tagline. Representaba solo el 20% del roster disponible en `_system/agency-agents/` — el 80% restante era invisible para `/triage` y `/delegate-issue`, lo que impedía que el grill panel sugiriera agentes existentes pero no registrados.

Eliminamos `employees.json` y reemplazamos el lookup por discovery en runtime: los skills escanean `_system/agency-agents/**/*.md`, derivan el slug desde el frontmatter `name` → kebab-case, y leen la `description` como tagline. Cualquier archivo `.md` en ese directorio es automáticamente un agente elegible.

`_system/agency-agents/` es un submodulo upstream (read-only), por lo que no es posible agregar flags `dispatchable: true` a los archivos. El discovery sin filtro es la única opción que no requiere un registry alternativo. Si en el futuro se necesita excluir agentes, la convención será moverlos fuera del directorio o usar un subdirectorio `_disabled/`.

## Consecuencias

- Agregar un agente = que su `.md` exista en `_system/agency-agents/`. No hay paso adicional.
- Los agent briefs existentes que referencian slugs (ej. `senior-developer`) siguen funcionando — el slug se deriva del campo `name` del frontmatter de forma determinística.
- El skill `/delegate` (general, no `/delegate-issue`) también referenciaba `employees.json` para rutas de repos. Ese skill se elimina por estar obsoleto — la delegación ahora usa subagentes nativos.
