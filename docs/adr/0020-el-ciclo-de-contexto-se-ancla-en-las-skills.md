# El ciclo de contexto se ancla en las skills, no en la prosa

El [ADR 0014](0014-el-problema-era-la-distribucion-no-la-composicion.md) creó el
Ciclo de contexto compartido y puso su mecánica en `context_sync.py`. El juicio de
cuándo usarla —traer al abrir, publicar en los cortes lógicos— quedó como prosa en
`INSTRUCTIONS.md`.

No se cumplió. La comprobación es directa: `context_sync.py status` encontró trabajo
sin publicar en cinco repos a la vez, incluidos cuatro commits sin subir en
`afin-webapp`, y en el workspace de una org el aporte más reciente de otra operadora
llevaba tres semanas sin que nadie lo trajera. Ninguna de las skills que abren una
sesión invocaba el script: `context_sync.py` no aparecía citado en un solo
`SKILL.md`.

Lo notable es que el propio script ya había diagnosticado este modo de falla, en su
docstring, sobre otra cosa:

> `log_command` se invoca por instrucción en 22 archivos SKILL.md y el registro
> subcuenta, así que sabemos que las instrucciones se cumplen a veces. Para un log
> alcanza; para traer el contexto de otro operador, no.

El argumento era correcto y la conclusión que se sacó fue la contraria a la que
pedía: se escribió un script para que la mecánica fuera confiable, y después se dejó
la decisión de invocarlo en el mismo lugar cuya falta de confiabilidad se acababa de
documentar. Una instrucción en prosa que ninguna skill ejecuta se cumple menos que
una que 22 skills invocan mal.

## Decisión

**Cada momento del ciclo es un paso numerado de la skill que abre ese momento.**

| Momento | Qué | Anclado en |
|---|---|---|
| Abrir o refrescar el día | traer | `/today` — Step 0 |
| Antes de leer el tracker | traer | `/triage`, `/delegate-issue` — Step 0 |
| Empezar un descanso | publicar | `/break <motivo>` |
| Volver de un descanso | traer | `/break back` |
| Cerrar la sesión | publicar | `/wrap-session` — Step 3 |

`INSTRUCTIONS.md` conserva la política y el porqué en un solo lugar, con la tabla de
momentos; lo que deja de tener es la responsabilidad de que el ciclo ocurra.

**Publicar deja de pedir confirmación.** La política anterior distinguía: traer no se
pregunta, publicar se ofrece. La distinción tenía sentido —publicar es visible para
terceros— pero su costo medido fue que no se publicara nada. Ahora se publica y se
reporta, una línea por repo, con el mensaje que la IA redacta por repo.

**El escaneo de material sensible se muda adentro de `push`.** Publicar
automáticamente significa `git add -A` sin que nadie mire, y el hook de pre-commit no
cubre estos repos: `staged_scan.instalar()` apunta `core.hooksPath` a un directorio
del harness, y los repos de contexto viven en `_data/` como repos aparte —ninguno de
los cinco lo tenía instalado—. `context_sync.push` ahora escanea el árbol de trabajo
con las mismas reglas de `.claude/rules/sensitive.json`, **antes** de tocar el índice,
y ante un hallazgo bloqueante devuelve el estado `sensible` sin commitear ni estagear
nada.

Escanear antes del `add` y no después es deliberado: revertir un staging que el
operador quizás armó a mano es otra forma de dejar un repo en un estado del que hay
que salir con comandos de git, que es exactamente lo que el ADR 0014 le reprochaba a
`/awi-sync`.

**`push` no publica desde una rama que no es la del manifiesto.** Al escribir este
ADR, `newhaze-webapp` estaba en `feat/hero-learn-flag` con el manifiesto declarando
`stg` — una rama de feature en un codebase es lo normal, no la excepción. El commit
habría ido a la rama activa y el `push origin stg` habría subido otra cosa: el
operador vería «publicado» con su trabajo intacto en local. Ahora eso devuelve el
estado `otra-rama` y no toca nada. Mergear o abrir un PR son decisiones del operador;
ninguna es del ciclo de contexto.

Este caso no existía como riesgo mientras publicar pedía confirmación, porque el
operador veía el repo antes de aceptar. Automatizar la publicación es lo que lo
convirtió en uno.

## `/wrap-session` cambia de orden

El gate de información sin guardar era el último paso, después de archivar la sesión
y de imprimir el resumen. Ahora es el primero, y se le agrega un barrido de trabajo
sin terminar —issues que el trabajo de hoy resolvió y siguen abiertos, decisiones sin
ADR, tareas a mitad de camino.

La razón es de dependencia, no de estética: lo que el operador decide guardar en ese
gate es contenido que el paso de archivado tiene que escribir y el de publicación
tiene que subir. Corriéndolo último, cualquier cosa que apareciera llegaba después de
un resumen que ya daba la sesión por cerrada.

## Qué no cambia

- **La mecánica.** `context_sync.py` sigue siendo el único lugar donde se hace git
  sobre repos de contexto.
- **Los conflictos.** Un `conflicto` se le muestra al operador y lo decide él. Un
  `sensible` también.
- **El alcance.** Los repos `upstream` siguen afuera del ciclo
  ([ADR 0012](0012-contextos-flotan-dependencias-pinean.md)), y el harness se
  actualiza con `/awi-update`.

## Cómo se verifica

```bash
python3 .claude/skills/shared/scripts/context_sync.py status
```

Si al cerrar una sesión eso devuelve algo distinto de «Todo publicado», el ciclo no
se cumplió. Es la misma comprobación que originó este ADR, y sirve como prueba
permanente.
