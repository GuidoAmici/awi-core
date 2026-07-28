# Los repos se declaran en manifiestos JSON y se materializan por clon, no como submódulos

Supersede a [ADR 0001](0001-gitmodules-is-ephemeral.md).

El ADR 0001 resolvió a medias un problema real: `.gitmodules` no puede versionarse en el raíz, porque el grafo de submódulos de un operador no es el de otro. La solución fue generarlo en cada máquina desde `user-submodules.json`. Pero eso dejó `.gitmodules` como un artefacto sintético que git seguía interpretando como configuración de submódulos, y mantuvo dos niveles con reglas distintas: el raíz sin gitlinks, y cada org workspace con gitlinks reales y su propio `.gitmodules` versionado.

Esa asimetría producía tres fallas concretas:

**El operador no podía elegir.** Materializar una org corría `git submodule update --init --recursive`, que arrastra todos sus codebases. Elegir un subconjunto exigía tocar el `.gitmodules` de la org — un archivo compartido, donde la elección de una persona se le impone al resto.

**El gitlink podía apuntar a la nada.** Un workspace fija el SHA exacto de cada codebase. Si el operador estaba parado en una rama local sin pushear, commitear ese gitlink dejaba al workspace apuntando a un commit irrecuperable para cualquier otro clon. Pasó, y no hay forma de recuperarlo salvo que alguien todavía tenga el objeto en disco.

**El comando de init estaba roto.** Al dejar de versionar los gitlinks de `_data/`, `git submodule update --init <path>` falla con `did not match any file(s) known to git`. No se notaba en máquinas ya inicializadas; rompía en todo bootstrap limpio.

Eliminamos los submódulos en ambos niveles. Nada en AWI es un submódulo: no hay gitlinks, no hay `.gitmodules`, no se llama a `git submodule` en ningún script. Cada repo se materializa con `git clone` y se oculta del repo que lo contiene vía `.gitignore` — `_data/` en el raíz, `codebase/*/` en cada org workspace. Es lo que evita la duplicación: el código está presente en el árbol pero es invisible para el índice del repo padre, así que un `git add -A` no puede tragárselo.

La declaración se parte en dos manifiestos, según quién es dueño del dato:

| Manifiesto | Dónde vive | Quién lo ve | Qué declara |
|---|---|---|---|
| `user-submodules.json` | `_data/users/<github-id>/` | solo ese operador | qué orgs y repos de sistema quiere, con url/path/branch, y de cada org qué codebases |
| `codebases.json` | `_data/organizations/<org>/` | versionado, todo el equipo | qué repos componen la org y en qué rama |

El corte es el punto: un workspace tiene que poder decirle a cualquier colaborador de qué está hecho, sin que la elección privada de nadie se filtre adentro. Antes esas dos cosas vivían en el mismo archivo y por eso se pisaban.

## Consecuencias

- Elegir codebases es por operador y no toca ningún archivo compartido: `/awi-submodule-toggle off <org>/<codebase>`.
- Se pierde el SHA fijado. Los workspaces siguen la punta de la rama declarada en vez de un commit exacto. Es una pérdida real de reproducibilidad, aceptada porque en la práctica el pin nunca se usó para volver a un estado anterior y sí causó el problema del commit irrecuperable.
- Apagar una entrada nunca borra el directorio. Sin gitlink, un checkout es dato común y borrarlo es un `rm -rf` sin red; los scripts pushean el trabajo local, avisan y dejan la decisión al operador.
- `sync_status.py` y `generate_gitmodules.py` desaparecen, junto con el mirror instancia → awi-core que ya había quedado sin objeto cuando la instancia pasó a *ser* awi-core.
- Un repo declarado en `user-submodules.json` pero ausente de `codebases.json` se reporta como advertencia en vez de ignorarse en silencio: casi siempre es un rename o un repo que se sacó de la org.
