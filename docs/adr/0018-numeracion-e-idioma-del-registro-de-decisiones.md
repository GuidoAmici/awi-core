# Numeración e idioma del registro de decisiones

El registro tenía cuatro números con problemas. `0005` y `0006` numeraban **dos
decisiones distintas cada uno**, y `0007` y `0008` eran **la misma decisión
duplicada** en inglés y en castellano. Un índice que debería ser la memoria del
sistema no podía citarse sin ambigüedad: «el ADR 0006» no identificaba nada.

Eso no es un problema de prolijidad. El [ADR 0013](0013-revision-integral-de-awi-core.md)
lo nombró como *«el propio registro perdió disciplina»*, y su costo es que una
referencia cruzada —de las que hay entre ADRs, en `CONTEXT.md`, en el `CHANGELOG`
y en los mensajes de commit— resuelve a la decisión equivocada o a ninguna.

## Decisión

**Un número identifica exactamente una decisión.** Las colisiones se resuelven
moviendo la decisión que tiene menos referencias existentes al primer número
libre del final del registro, no reordenando el registro entero.

**Idioma único: castellano**, que es el de los ADRs recientes y del operador. Los
duplicados en inglés se eliminan, no se traducen: el castellano ya existía y
tenía las referencias. Los ADRs que **sólo** existen en inglés se dejan como
están — reescribir un registro histórico es peor que tenerlo en dos idiomas.

**El número es un identificador, no una fecha.** `0016` y `0017` son de marzo y
abril de 2026, anteriores a `0009`. Renumerar en orden cronológico habría roto
todas las referencias existentes para ganar una propiedad que ningún consumidor
usa.

## Mapeo viejo → nuevo

Los mensajes de commit no se pueden actualizar, así que el mapeo se registra acá:
una referencia histórica sigue siendo resoluble leyendo esta tabla.

| Antes | Ahora | Qué pasó |
|---|---|---|
| `0005-solution-package-commit-model.md` | `0005-solution-package-commit-model.md` | se queda: tiene las referencias existentes |
| `0005-standard-git-flow-over-tool-identity-branches.md` | `0016-git-flow-estandar-en-lugar-de-ramas-por-herramienta.md` | movido |
| `0006-fetch-issues-as-shared-data-layer.md` | `0006-fetch-issues-as-shared-data-layer.md` | se queda: está en castellano y tiene la referencia de `fetch_issues.py` |
| `0006-user-org-relationship-lives-in-user-space.md` | `0017-la-relacion-usuario-org-vive-en-el-espacio-del-usuario.md` | movido |
| `0007-awi-core-como-source-of-truth.md` | `0007-awi-core-como-source-of-truth.md` | se queda |
| `0007-awi-core-as-source-of-truth.md` | — | eliminado, duplicado en inglés |
| `0008-agent-discovery-desde-agency-agents.md` | `0008-agent-discovery-desde-agency-agents.md` | se queda |
| `0008-agent-discovery-over-employees-registry.md` | — | eliminado, duplicado en inglés |

## Convención, de acá en adelante

1. **Un archivo, un número, una decisión.** El próximo ADR toma el número libre
   más alto.
2. **Castellano.** El título es una oración que afirma la decisión, no un tema:
   «Dos ramas porque el gate vive en el servidor», no «Estrategia de ramas».
3. **El nombre del archivo describe la decisión**, así que un enlace roto se
   nota al leerlo.
4. **Una decisión que reemplaza a otra la enmienda por escrito**, con enlace en
   las dos direcciones. No se edita la decisión vieja para que parezca que nunca
   se tomó.
5. **La integridad la verifica un test**, no la vigilancia: que no haya dos
   archivos con el mismo número y que todo enlace entre ADRs resuelva a un
   archivo existente. Es lo que hizo segura esta renumeración — se corrió antes y
   después de cambiar los números. Ver `tests/test_adr_registry.py`.

## Qué la falsaría

Si aparece un consumidor que necesita que el número ordene cronológicamente —un
generador de changelog, o un índice que se lea de corrido como narrativa—, la
decisión de tratar el número como identificador puro se reabre, y el precio de
renumerar todo pasa a estar justificado.

## Consecuencias

- `CONTEXT.md`, el `CHANGELOG` y las referencias en las skills siguen resolviendo:
  el mapeo se eligió para que ninguna referencia existente se rompiera.
- Los dos ADRs eliminados no pierden contenido: su versión en castellano es la
  que se conserva y dice lo mismo.
- El registro pasa de 19 archivos con 4 números ambiguos a 18 archivos con 18
  números únicos.
