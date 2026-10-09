# Cada org declara sus MCP y AWI los compone

> **Estado: aceptado (2026-10-09).** Lo pidió el operador al elegir la opción B entre
> dos: dejar los MCP de cada org en el `.mcp.json` de AWI, o que cada org los declare en
> su propio repo.

## El problema

El conector de Supabase de claude.ai deja de funcionar cuando el operador cambia de
cuenta de Claude, así que New Haze pasó a tener un MCP propio, `supabase-newhaze`, con
su llave en una variable de entorno. Quedó en el `.mcp.json` de AWI, junto al
`supabase` de Afin y a los MCP que no son de ninguna org.

Eso mezcla dos cosas: la configuración de la herramienta y la de cada organización.
Un MCP de New Haze viaja a cualquiera que clone AWI, y desactivar una org no saca sus
MCP. Es el mismo corte que el [ADR 0009](0009-manifiestos-json-en-lugar-de-submodulos.md)
hizo con los codebases: lo de la org vive en el repo de la org.

Pero no alcanza con mover el archivo. **Claude Code sólo lee el `.mcp.json` de la raíz
del proyecto.** Uno dentro de `_data/organizations/<org>/` no lo carga ninguna sesión
que trabaje desde AWI.

## La decisión

- Cada org declara sus MCP en `mcp.json`, en la raíz de su repo, con la misma forma
  que `.mcp.json`.
- Los MCP que no son de ninguna org viven en `.mcp.base.json`, versionado en AWI.
- `.claude/skills/shared/scripts/mcp_compose.py` arma el `.mcp.json` de la raíz con la
  base y las orgs **activas** de `user-submodules.json`. `.mcp.json` queda generado y
  fuera de git: se edita la base o el `mcp.json` de la org, nunca el resultado.
- Un nombre repetido es un error: una org no pisa un MCP de AWI ni de otra org.
- `/awi-initialize` recompone al terminar de materializar. Claude Code toma el cambio en
  la sesión siguiente o desde `/mcp`.
- Ningún `mcp.json` guarda secretos: las llaves van como `${VARIABLE}`.

## Lo que se movió

| MCP | Antes | Ahora |
|---|---|---|
| `supabase` (Afin, `${AFIN_SUPABASE_PAT}`) | `.mcp.json` de AWI | `afin-org/mcp.json` |
| `supabase-newhaze` (`${NEWHAZE_SUPABASE_EDIT}`) | `.mcp.json` de AWI | `newhaze-org/mcp.json` |

El resto quedó en la base. Algunos podrían ser de una org (`arca-afip`, `mercadopago`,
`meta-ads`, el `filesystem` con la carpeta Blender de New Haze); moverlos es decisión
del operador, y se hace llevando su bloque al `mcp.json` de la org y corriendo el script.

## Consecuencias

- Una org desactivada deja de aportar sus MCP en la próxima composición.
- Un clon nuevo no tiene `.mcp.json` hasta correr `/awi-initialize` o el script.
- `mcp_compose.py --check` sale con 1 si el `.mcp.json` en disco no coincide con lo que
  generaría; sirve para detectar una edición a mano del resultado.
