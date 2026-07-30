# Descubrimiento de agentes desde _system/agency-agents/ en lugar de employees.json

`employees.json` era un registry manual que listaba qué agentes eran dispatchables, con su path y tagline. Representaba solo el 20% del roster disponible en `_system/agency-agents/` — el 80% restante era invisible para `/triage` y `/delegate-issue`, lo que impedía que el grill panel sugiriera agentes existentes pero no registrados.

Eliminamos `employees.json` y reemplazamos el lookup por discovery en runtime: los skills escanean `_system/agency-agents/**/*.md`, derivan el slug desde el frontmatter `name` → kebab-case, y leen la `description` como tagline. Cualquier archivo `.md` en ese directorio es automáticamente un agente elegible.

`_system/agency-agents/` es un submodulo upstream (read-only), por lo que no es posible agregar flags `dispatchable: true` a los archivos. El discovery sin filtro es la única opción que no requiere un registry alternativo. Si en el futuro se necesita excluir agentes, la convención será moverlos fuera del directorio o usar un subdirectorio `_disabled/`.

## Consecuencias

- Agregar un agente = que su `.md` exista en `_system/agency-agents/`. No hay paso adicional.
- Los agent briefs existentes que referencian slugs (ej. `senior-developer`) siguen funcionando — el slug se deriva del campo `name` del frontmatter de forma determinística.
- El skill `/delegate` (general, no `/delegate-issue`) también referenciaba `employees.json` para rutas de repos. Ese skill se elimina por estar obsoleto — la delegación ahora usa subagentes nativos.

## Enmienda del 2026-07-30 — la migración se completó

Esta decisión se tomó y no se ejecutó: `employees.json` siguió existiendo con 36
entradas y siendo leído por `/delegate-issue`, `/grill-with-docs`, el template de
Agent Brief y `delegation.md`. Es una instancia del patrón que el
[ADR 0013](0013-revision-integral-de-awi-core.md) diagnosticó — migraciones a
medias que dejan residuo activo — y por eso el PRD 3 ([#82](https://github.com/GuidoAmici/awi-core/issues/82))
la incluyó.

El registro está eliminado. El descubrimiento vive en
`.claude/skills/shared/scripts/agent_personas.py`, con dos ajustes sobre lo que
esta decisión describía:

**El slug se deriva del nombre del archivo, no del campo `name` del
frontmatter.** El `name` es prosa en mayúsculas («AI Engineer»), y pasarla a
kebab-case no siempre reproduce el slug con el que los Agent Brief existentes
referencian a la persona. El nombre del archivo sin su prefijo de categoría sí:
`engineering/engineering-ai-engineer.md` → `ai-engineer`.

**Un archivo `.md` sin frontmatter no es una persona-agente.** «Cualquier `.md`
en ese directorio es automáticamente un agente elegible» es demasiado amplio: el
repo trae playbooks y documentos de proyecto. Exigir `name` o `description`
distingue una persona de un documento — y es exactamente lo que el registro
eliminado no hacía, porque listaba `nexus-strategy`, un playbook sin frontmatter,
como si fuera un agente.

Lo que la migración midió, y que refuerza la decisión original: de las 35 entradas
del registro, **33 resolvían y 2 estaban rotas** — una apuntaba a un archivo
inexistente y la otra a ese playbook. Un registro escrito a mano sobre un árbol
de 292 archivos que un tercero puede cambiar sin aviso está desactualizado por
construcción. El árbol descubre 280 personas contra las 35 que el registro
listaba.

Verificado en `tests/test_agent_personas.py`, que asevera contra el árbol real
que las claves del registro eliminado siguen resolviendo: sin eso, borrarlo
habría roto cada Agent Brief ya escrito en un issue.
