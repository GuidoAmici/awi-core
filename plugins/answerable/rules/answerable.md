# answerable

Cómo se estructura una respuesta para que el lector pueda contestarla señalando,
en vez de reescribirla. Rige desde este turno, en toda respuesta al operador y en el
informe final de un subagente al agente principal.

Este archivo es la norma y se inyecta entero en cada sesión. El porqué de cada regla,
los ejemplos completos y los casos que las motivaron están en
[answerable-detalle.md](answerable-detalle.md): leelo cuando dudes cómo aplicar una.
Si los dos difieren, manda éste.

## Cinco bloques

Cada bloque es un encabezado `##`, en este orden. Si el operador preguntó algo, el
bloque que lo contesta abre la respuesta.

| Bloque | Qué va adentro |
|---|---|
| **Qué hice** | Lo que creé, modifiqué o borré, y dónde |
| **Qué tenés que saber** | Lo que averigüé o detecté y el operador no sabía |
| **Hilos abiertos** | Lo que esta sesión empezó y no terminó |
| **Qué propongo** | Lo que podría hacer después y no empecé |
| **Qué necesito de vos** | Lo que no puedo resolver solo |

**Ningún ítem cae en dos bloques.** Cada frontera es una pregunta binaria:

- **Hice o saber — ¿quedó algo distinto en disco, repo o issue?** Si sólo cambió lo que sabemos (leí, medí, deduje), es hallazgo.
- **Hice o hilo — ¿quedó terminado?** Lo hecho a medias va en los dos: la parte verificable en «Qué hice», lo que falta en el hilo. En código, terminado es *en el remoto compartido*: un commit sin pushear o un PR sin mergear es hilo.
- **Hilo o propuesta — ¿ya empezó, o el operador ya la aceptó?** Entonces es hilo.
- **Propuesta o pregunta — ¿puedo avanzar sin la respuesta?** Si no, va a «Qué necesito de vos», con número.

**Lo que pidió el operador no cambia de bloque, cambia de orden:** una comparación
para que elija va a «Qué necesito de vos»; con recomendación, a «Qué propongo»; la
información buscada, a «Qué tenés que saber»; el reporte de lo hecho, a «Qué hice».

**Los bloques vacíos se omiten, menos «Qué necesito de vos»:** vacío se declara
("No necesito nada de vos, sigo"). Una confirmación o una respuesta de un párrafo no
se estructura.

## Cada ítem abre con su TLDR en negrita

Leer sólo las negritas tiene que alcanzar para tener la respuesta entera.

```markdown
- **La afirmación:** la evidencia, el detalle, la consecuencia.
```

- Viñetas sin letras ni códigos ([ADR 0025](../../../docs/adr/0025-las-preguntas-llevan-numero-y-los-items-no-llevan-letra.md)). Sin tope de ítems.
- El TLDR **afirma, no anuncia**, entra en una línea y nombra la cosa (el número, el archivo, la decisión), no su categoría. Sin pronombres de suspenso ("esto", "la clave acá").
- Una sola negrita por ítem. Un ítem de una oración es todo TLDR y no lleva negrita.
- El detalle toma la forma del contenido: tabla si hay dos o más cosas por dos o más atributos, lista numerada si el orden importa, bloque de código para código, bloque pegable para lo que se corre, prosa sólo para razonar. Nada de formato de adorno; la tabla va debajo de su TLDR.

## Las preguntas tienen número fijo

- Cada pregunta recibe el próximo número libre de la sesión y lo conserva. Un número no se reusa ni se corre: si quedan la 21 y la 23, se escriben 21 y 23.
- El número va dentro de la negrita: `- **52. ¿La página enlaza al tema 5?**`. Una línea que empieza con `52.` la renumera Markdown.
- Se agrupan por módulo, con un `###` por grupo.
- Las no contestadas vuelven enteras en cada turno: número, pregunta, contexto, opciones y recomendación. Una que dejó de importar se retira diciéndolo.
- El operador contesta «22. Sí». Al actuar, nombrá la pregunta en pocas palabras; si el número no coincide con ninguna abierta, confirmá antes.
- La numeración sobrevive a la sesión. Un subagente no numera: numera quien le habla al operador.
- Con preguntas abiertas no se espera: hacé todo lo que no depende de la respuesta, y cada pregunta dice qué frenó.

## El reporte y los hilos se acumulan

- Mientras el operador no contesta, cada mensaje es el mismo reporte con lo nuevo agregado al final de su bloque y marcado «(nuevo)». Cuando contesta, empieza un reporte nuevo. Si se refiere a algo de un reporte ya contestado, confirmá qué entendiste.
- Los hilos abiertos son de la sesión entera y dicen dónde quedó el trabajo (qué está hecho, qué falta y dónde), no qué se pensaba hacer.
- Un hilo sale sólo de tres maneras: se cierra (pasa a «Qué hice»), el operador lo abandona (confirmá antes de borrarlo) o se convierte en issue, con su enlace.

## Los documentos abren con TLDR

Un documento más largo que un párrafo —issue, PR, ADR, BDR, PRD, output, artifact,
brief a un subagente, copy de marca— abre con cuatro líneas: **qué quiero**, **qué
querés que haga**, **qué obtiene** y **por qué vale la pena**. Ni más ni menos. La
segunda nunca se omite: si no hay pedido, se declara vacía. No aplica a turnos de
conversación ni a mensajes de commit.

## Ningún identificador viaja desnudo

- Todo identificador opaco que traigas (issue, PR, ADR, BDR, PRD, SHA, corrida de CI, milestone) llega clickeable y con una paráfrasis de una frase de qué plantea, no su título. Si lo escribió el operador, sobra la paráfrasis, no el enlace. Se enlaza la primera vez que aparece.
- **Issues y PRs en una respuesta los enlaza linkify:** se escriben como referencia sola en texto corrido, nunca entre backticks. `#63` o `PR#63` si viven en el repo del directorio de trabajo (en la raíz de AWI, `awi-core`); `newhaze-webapp#63` en otro repo del mismo dueño; `owner/repo#63` si el dueño es otro.
- Todo lo demás, y todo texto fuera de la conversación, va como link Markdown con la URL completa: `…/issues/<n>`, `…/pull/<n>`, `…/commit/<sha>`, `…/actions/runs/<id>`. ADR, BDR y outputs, con su ruta relativa al repo. En un cuerpo de GitHub, `owner/repo#63` se enlaza solo y el nombre corto no.
- Leé antes de mencionar: `gh issue view` para uno, `gh issue list --json number,title,body` para varios. Traé sólo los que están en juego y decí cuántos dejaste afuera.
- Los mensajes de commit quedan fuera de esta regla.

## Un comando para el operador se pega y corre

- Arranca con `cd` a la ruta absoluta, también dentro de `_data/`, porque sus repos son repos aparte.
- Un bloque por tarea, con los pasos encadenados con `&&`. No hereda estado de otro bloque.
- Sin `$` de prompt ni salida esperada adentro. Las explicaciones van afuera o como comentarios `#`.
- Lo que asume del entorno se verifica con un guard: `: "${VAR:?definí VAR antes de correr esto}"`. Una secuencia con credenciales va en subshell `( … )`; nunca `set -e`; las variables, entre comillas.
- Los valores van resueltos y literales. Un placeholder es el último recurso: en `MAYÚSCULAS` y explicado arriba del bloque. Un secreto viaja sólo como nombre de variable.
- Si es destructivo, pide `sudo` o toca algo compartido, avisalo en una línea antes.
- Un comando citado como ilustración no necesita ser pegable: decilo al introducirlo.
