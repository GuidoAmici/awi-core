# answerable

Cómo se estructura una respuesta para que el lector pueda contestarla señalando,
en vez de reescribirla.

Estas reglas rigen desde este turno, en toda respuesta al operador y en el informe
final de un subagente al agente principal.

## Toda respuesta tiene cinco bloques con dirección

Una respuesta larga puede tener todo lo que el operador necesita y aun así no decirle dónde está nada. El resultado del pedido aparece a mitad de un párrafo, la sugerencia que había que aprobar quedó entre dos hallazgos, y para contestar "sí a lo segundo" hay que reescribir lo segundo. **La estructura no es cortesía tipográfica: es lo que vuelve la respuesta contestable.**

Cinco bloques, siempre en este orden —salvo que el operador haya preguntado algo, y entonces el bloque que contesta abre la respuesta:

| Letra | Bloque | Qué va adentro |
|---|---|---|
| `A` | **Qué hice** | Lo que creé, modifiqué o borré, y dónde |
| `B` | **Qué tenés que saber** | Lo que averigüé o detecté y el operador no sabía |
| `C` | **Hilos abiertos** | Lo que esta sesión empezó y no terminó |
| `D` | **Qué propongo** | Lo que el agente podría hacer después y no empezó |
| `E` | **Qué necesito de vos** | Lo que el agente no puede resolver solo |

### Los cinco bloques son un solo eje

El eje es **el grado de cierre**. `A` y `B` están cerrados: lo hecho no vuelve a hacerse y un hallazgo no pide nada. `C` está abierto y empezado. `D` y `E` están abiertos y sin empezar — y de esos dos, `D` lo puede cerrar el agente y `E` sólo el operador.

**Ningún ítem cae en dos bloques**, porque cada frontera es una pregunta binaria que se contesta al escribir el ítem:

- **`A` o `B` — ¿quedó algo distinto?** Si el disco, el repo o un issue quedaron cambiados, es `A`. Si no —leí, busqué, medí, deduje—, es `B`. "Revisé los tres handlers y no hay bug" es `B`: lo único que cambió es lo que sabemos.
- **`A` o `C` — ¿quedó terminado?** Un trabajo a medias produce las dos cosas: `A` reporta la parte que sí quedó y es verificable en el repo, `C` dice qué falta. El hilo no repite lo hecho.
- **`C` o `D` — ¿ya empezó?** Una propuesta que nunca se tocó es `D`. En cuanto se empieza —o el operador acepta un `D` y todavía no se ejecutó— pasa a ser un hilo.
- **`D` o `E` — ¿puedo avanzar sin la respuesta?** Ver más abajo.

Un bloque que necesita un "y después" adentro de su definición son dos bloques.

**Para código, "terminado" es "en el remoto compartido", no "committeado localmente".** Un commit sin pushear, un PR abierto esperando tests o CI, o un PR ya testeado y aprobado sin mergear son `C`, aunque el commit ya exista y esté reportado en `A`. El ítem de `A` cuenta qué se hizo; el de `C` dice que todavía no llegó a destino, citando la dirección del primero: «`C3`. El commit de `A2` sigue sin pushear — CI de `newhaze-webapp` corriendo».

### Cada ítem lleva su dirección

Los ítems se numeran dentro de su bloque, y **el tag va en el ítem, no en el título**: el bloque se titula `## Qué propongo` y sus ítems son `D1`, `D2`, `D3`. Repetir la letra en el encabezado no agrega nada — el ítem ya la trae.

La dirección existe para que el operador conteste sin reescribir. «`D3`, aplicalo, el resto no» es una respuesta completa.

- **La letra pertenece al bloque, no al lugar.** Las propuestas son `D` aunque falten `A`, `B` y `C`. Una dirección que cambia de significado según el turno no es una dirección.
- **Los cinco bloques numeran sus ítems**, `B` incluido. Un hallazgo que no se puede citar no se puede objetar.
- **Los bloques se citan entre sí por dirección.** Un hilo frenado por una decisión lo dice: «`C2` … frenado por `E1`». Es la ventaja de tener direcciones y no cuesta nada.
- **Sin tope de ítems.** Curar sigue siendo parte del trabajo, pero esconder una propuesta para respetar un número es peor que una lista larga.
- **Valen para el último turno.** Cada respuesta renumera desde `1`. Si el operador se refiere a un turno anterior, el agente confirma qué entendió antes de actuar.

### Cada ítem abre con su TLDR en negrita

**Leer sólo las negritas de una respuesta tiene que alcanzar para tenerla entera.** Todo lo demás es evidencia, para lo que el operador quiera auditar. Es la misma regla de la sección siguiente —el TLDR va primero— una escala más abajo: del texto al ítem.

El formato es fijo:

```markdown
A1. **La afirmación:** la evidencia, el detalle, la consecuencia.
```

- **El TLDR afirma, no anuncia.** Si le podés poner "Sobre" adelante y suena a título de sección, es un rótulo y no sirve. *"La tercera vía de salida es la que resuelve tu problema"* anuncia; *"Un hilo que no cerrás hoy sale como issue, y ese issue es el handoff"* afirma. El rótulo obliga a leer el párrafo para saber de qué se hablaba, que es exactamente lo que el formato existe para evitar.
- **Test del borrado.** Tapá el detalle. Si el TLDR sigue siendo verdadero y útil solo, está bien escrito. Si deja al operador sin saber de qué se hablaba, es un anzuelo, no un resumen.
- **Nombrá la cosa, no su categoría.** El dato entra en el TLDR: el número, el archivo, el nombre, la decisión. "Faltan `billing.ts` y `webhooks.ts`" y no "quedaron archivos pendientes".
- **Sin pronombres de suspenso.** "Esto", "la clave acá", "lo que resuelve el problema", "el punto importante" — todos refieren a algo que sólo aparece en el detalle. Es la forma más común del acertijo y la más fácil de detectar al releer.
- **Una sola negrita por ítem, la del TLDR.** Si el detalle también resalta, no queda nada que escanear.
- **El detalle es opcional.** Un ítem que entra en una oración es todo TLDR y no lleva negrita: `A5. Commit 8139bcc, en dev.` El formato aplica cuando hay algo que resumir.

**Una línea.** Si el TLDR no entra en una, casi siempre es porque empezó a contar el detalle.

### El detalle toma la forma de su contenido

El TLDR es siempre una línea de prosa en negrita — eso no se negocia, porque escanear las negritas tiene que seguir alcanzando para tener la respuesta entera. **El detalle, en cambio, no tiene forma fija: toma la del contenido.**

| Si el contenido es | El detalle es |
|---|---|
| Dos o más cosas comparadas por dos o más atributos | Una tabla |
| Pasos donde el orden importa | Una lista numerada |
| Código, un diff, una estructura | Un bloque de código |
| Algo que el operador va a correr | Un bloque pegable |
| Un argumento con hilo causal | Prosa |

**La prosa es para razonar, no para enumerar.** El modo de falla más común es escribir en párrafo una comparación que era una tabla: si el detalle repite los mismos atributos para cada cosa —"la opción A cuesta X y tarda Y; la opción B cuesta Z y tarda W"—, ya es una tabla, sólo que escrita peor.

**El formato tampoco se agrega de adorno.** Una tabla de una fila es una oración. Tres viñetas de una oración cada una son un párrafo. Si la forma no le ahorra una lectura al operador, no va.

**La forma no cambia la dirección.** Un ítem con tabla sigue siendo un ítem: lleva su letra, su número y su TLDR arriba, y la tabla va abajo, sin indentar. Una tabla suelta —sin la línea que dice qué concluye— obliga a leerla entera para saber de qué se hablaba, que es el mismo acertijo que el TLDR existe para evitar.

### Lo que contesta la pregunta va primero en la respuesta

Los bloques clasifican por **tipo de contenido**, no por destinatario, así que no hay un bloque "lo que preguntaste". Lo que el operador pide ya tiene destino, y el destino lo decide qué es la respuesta, no quién la pidió:

| Lo que pidió el operador | Dónde va | Por qué |
|---|---|---|
| Una comparación para que elija él | `E` | No se puede avanzar sin su decisión |
| Una comparación con una recomendación | `D` | Es una propuesta; la comparación es su detalle |
| Información que el agente fue a buscar | `B` | Lo único que cambió es lo que sabemos |
| El reporte de algo que se hizo | `A` | El entregable ya está en el repo |

**Que lo hayan pedido no cambia el bloque, cambia el orden.** "Revisé los tres handlers y no hay bug" es `B` de las dos maneras; lo que cambia es que, si el operador preguntó justamente eso, es `B1` y `B` abre la respuesta.

**El bloque que contesta se imprime primero y conserva su letra.** `B` arriba de `A` se sigue llamando `B`. Es la misma idea que ya rige las direcciones —la letra pertenece al bloque, no al lugar—, usada acá para lo que hace falta: que la respuesta no haya que ir a buscarla. Una respuesta que la esconde adentro de una lista larga falla igual que una sin estructura.

### `C` es lo único que no se renumera desde cero

Los otros cuatro bloques valen para el último turno. **Los hilos abiertos son de la sesión entera:** un hilo que se abrió en el tercer turno sigue apareciendo en el noveno hasta que se cierre. La numeración se rehace en cada respuesta; la lista, no.

Esa persistencia es todo el punto del bloque. Sin ella, repartir el trabajo entre sesiones obliga a reconstruir al final lo que se fue abriendo al principio — y en una sesión larga los primeros hilos ya no están en contexto para reconstruirlos.

**Un hilo dice dónde quedó, no qué se pensaba hacer.** "Empecé a migrar los handlers" no se puede retomar. "La migración tiene los tres primeros hechos en `auth.ts`; faltan `billing.ts` y `webhooks.ts`, con el mismo patrón" sí.

**Un hilo sale de la lista de tres maneras**, y sólo de esas tres:

1. **Se cierra** — pasa a `A` en el turno que lo termina, y desaparece de `C`.
2. **Se abandona** — el operador dice que no va, y el agente lo confirma antes de borrarlo.
3. **Se convierte en issue** — si el hilo va a sobrevivir a la sesión, deja de ser un hilo y pasa al tracker, con su enlace. Es la vía normal para repartir trabajo entre sesiones.

`C` es lo que consume el ritual de cierre de sesión, que sin esa lista la reconstruye barriendo la conversación entera al cerrar. Mantenerla turno a turno hace ese barrido una verificación en vez de una reconstrucción.

### Los bloques vacíos se omiten, menos `E`

Un bloque sin contenido no se rotula. Si el agente no tocó nada, `A` no aparece y la respuesta abre en `B`.

**`E` es la excepción: cuando está vacío, se declara.** "No necesito nada de vos, sigo" es información; borrar el bloque deja al operador preguntándose si le toca algo. Es la misma razón por la que la línea 2 del TLDR nunca se omite.

### Propuesta y decisión se separan por una sola pregunta

**¿Puedo avanzar sin la respuesta?** Si sí, es `D`. Si no, es `E`.

El criterio es binario y se evalúa al escribir el ítem, no al terminar la respuesta. Una propuesta que el operador ignora no traba nada; una decisión que ignora deja trabajo detenido — y por eso las dos no pueden vivir en el mismo bloque, aunque las dos terminen en "¿lo hago?".

**`E` no es sólo información.** Una decisión entre dos caminos, la conformidad sobre algo ya hecho y un dato que sólo el operador tiene son los tres el mismo bloque: cosas que el agente no puede resolver por su cuenta.

**Con `E` abierto el agente no se sienta a esperar.** Hace todo lo que no dependa de la respuesta, frena únicamente lo que sí, y `E` dice qué quedó detenido y qué siguió igual. Volver con las manos vacías por una pregunta que afectaba a un tercio del trabajo es un modo de falla, no prudencia.

### Dónde aplica

En las respuestas al operador y en el informe final de un subagente al agente principal: los dos son turnos de conversación. Un documento no es un turno — issues, PRs, ADR, BDR, outputs, PRD, artifacts y briefs a subagentes abren con el TLDR de la sección siguiente.

**El piso es más de un párrafo.** Una confirmación o una respuesta de una línea no se estructura: ahí el mensaje entero es un solo ítem y no necesita rótulo.

En el ejemplo el operador preguntó *"¿unifico la guarda o dejo la copia en cada handler?"*, así que `D` abre la respuesta sin dejar de llamarse `D`, y la comparación que la contesta va como tabla y no como párrafo:

```markdown
## Qué propongo
D1. **Unificar la guarda gana por mantenimiento y pierde por riesgo de
    regresión**, y con los 42 tests en verde el riesgo es el barato:

| | Unificar en `guard.ts` | Dejar la copia |
|---|---|---|
| Handlers a tocar | 3 | 0 |
| Riesgo de regresión | Medio | Nulo |
| El próximo handler | Hereda el fix | Copia el bug |

D2. **Un issue por los tres handlers duplicados**, y cierro `C1` con él.

## Qué hice
A1. **El fix del token expirado quedó en `auth.ts:42`:** los 42 tests
    pasan y no hizo falta tocar el middleware.

## Qué tenés que saber
B1. **El mismo bug vive en `billing.ts`, `webhooks.ts` y `export.ts`:**
    los tres copian la guarda en vez de llamarla.

## Hilos abiertos
C1. **La guarda unificada resuelve sesión expirada y le faltan dos casos:**
    token inválido y refresh, los dos en `guard.ts`.
C2. **El renombre de `UserCtx` quedó a mitad, frenado por `E1`:** los
    imports ya apuntan al nombre nuevo, las definiciones no.

## Qué necesito de vos
E1. **¿`UserCtx` pasa a `Principal` o a `Actor`?** Frena `C2`; el resto
    del renombre no depende de la respuesta y siguió.
```

Las otras reglas de escritura siguen valiendo adentro de los bloques: ningún identificador viaja desnudo, y un comando dirigido al operador se pega y corre.

## El TLDR va primero

Concepto tomado de Alex Hormozi. Un texto que no dice de qué va en las primeras líneas obliga al lector a armar el contexto mientras lee, y esa carga se paga **antes** de que haya podido evaluar nada. La claridad no es un resumen que se agrega al final: es lo primero que se escribe.

Cuatro líneas, en este orden:

| # | Línea | Qué responde |
|---|---|---|
| 1 | **Qué quiero** | La tesis o el pedido, en una frase |
| 2 | **Qué querés que haga** | La acción concreta que le toca al lector |
| 3 | **Qué obtiene** | El resultado, desde el lado del lector |
| 4 | **Por qué vale la pena** | Lo que vuelve razonable el intercambio |

**Nada más, nada menos.** Los dos modos de falla son simétricos y los dos cuestan igual: si falta una línea el lector no puede decidir —sabe qué le pedís pero no qué gana, o al revés—; si sobra contexto, el ruido tapa las cuatro que sí importaban. Un TLDR de seis líneas no es un TLDR más completo, es uno peor.

### Cuando el texto no es un pedido

La plantilla nace de una oferta, así que en un reporte hay que traducirla: la línea 1 pasa a ser qué se hizo o qué se propone. **La línea 2 nunca se omite — se declara vacía.** "No necesito nada de vos, es para que estés al tanto" es información; borrar la línea deja al lector preguntándose si le toca algo.

### Dónde aplica

En la apertura de cualquier **texto escrito** que un humano vaya a leer y que sea más largo que un párrafo: cuerpos de issues y PRs, PRD, BDR, ADR, outputs, briefs a subagentes, artifacts —arriba de la capa de escaneo— y copy de marca. En un artifact o un issue el TLDR puede ser un bloque de cuatro líneas rotuladas; en un output suele ser un párrafo corto que las contiene sin rotularlas.

**No aplica a los turnos de conversación** —respuestas al operador, informe final de un subagente—. Ahí manda el orden de la sección anterior: `A1` o `B1` ya abren diciendo de qué va, y encimarles un TLDR duplica la apertura. La regla es "¿es un turno o es un documento?".

Tampoco aplica a mensajes de commit —el scope de Conventional Commits ya cumple esa función y el subject tiene límite—, ni a textos de una línea o confirmaciones, donde el mensaje entero ya es el TLDR.

**No reemplaza la paráfrasis del identificador** de la sección siguiente: un TLDR que dice "cerrar #47" sigue sin decir nada. Las dos reglas se aplican juntas.

### Marca y copy

La bajada a copy de cara al consumidor —headline, CTA, promesa, prueba— está en [references/tldr.md](references/tldr.md). El TLDR pone el esqueleto; la voz y la forma siguen siendo las del Design System de la org destinataria.

## Ningún identificador viaja desnudo

Un `#63`, un `ADR 0021` o un `d0f96fd` no dicen nada por sí mismos: son direcciones, no información. El operador no memoriza el backlog, y un agente que escribe "esto lo cubre #47" está pidiendo que alguien vaya a buscar qué plantea #47 para poder seguir la frase.

**Todo identificador que traiga el agente a la conversación va acompañado de qué plantea.** Si el identificador lo escribió el operador, ya sabe de qué habla — no hace falta repetírselo.

### Qué cubre

Cualquier identificador opaco: issues, PRs, ADR, BDR, PRD, SHAs de commit, milestones. No es una lista cerrada; el criterio es si el identificador, leído solo, dice de qué se trata.

### Qué acompaña al identificador

Una **paráfrasis de una frase**, en el idioma de la conversación — no el título literal. Los títulos son etiquetas de tracker ("pgTAP", "variantes"); la paráfrasis dice qué está en juego.

Referencia primero, tema después:

```
newhaze-webapp#63 — soporte de variantes de producto en el panel B2B
ADR 0021 — la progresión se registra como eventos, no como estado
d0f96fd — el commit que sacó los codebases del ciclo automático de sync
```

Cross-repo, el identificador lleva el repo: `newhaze-webapp#63`. Dentro del repo en curso, `#63` alcanza.

### Leer antes de mencionar

**No se parafrasea desde el título ni de memoria.** Un artefacto se lee antes de nombrarlo: `gh issue view <n> --repo <owner/repo>` para uno solo, `gh issue list --json number,title,body` para varios en una sola llamada, y los ADR/BDR son archivos locales.

Traer treinta issues enteros satura el contexto sin ayudar a nadie. Traé los que están en juego, y decí cuántos dejaste afuera y por qué — curar es parte del trabajo, no un atajo.

### Dónde aplica

En las respuestas al operador y en todo texto que vaya a leer un humano: comentarios en issues, ADR, BDR, outputs, cuerpos de PR. Los mensajes de commit quedan fuera — el scope de Conventional Commits ya cumple esa función y el subject tiene límite de caracteres.

## Un comando que le pasás al operador se pega y corre

Todo bloque de shell dirigido al operador es **autocontenido**: se copia entero, se pega en una terminal cualquiera y funciona. Sin editarlo, sin adivinar desde qué carpeta correrlo, sin haber corrido antes otro bloque de la misma respuesta.

El modo de falla es cotidiano y siempre el mismo: el agente conoce su directorio de trabajo y escribe el comando desde ahí, pero el operador está en otra terminal, en otra carpeta, a veces en otro repo. Pega, falla, y tiene que pedir el `cd` que faltaba. **La ruta la sabe el agente — pedírsela al operador es devolverle trabajo ya hecho.**

### Qué cumple un bloque pegable

- **Arranca con `cd` a la ruta absoluta** del directorio donde corresponde ejecutarlo. Absoluta, no relativa: no se sabe dónde está parado el operador. Vale también dentro del vault — los repos de `_data/` son repos aparte, y un comando de git contra el repo equivocado no falla, hace otra cosa.
- **Un solo bloque por tarea.** Varios pasos se encadenan con `&&` o van en líneas seguidas dentro del mismo bloque. Tres bloques que hay que pegar en orden son tres oportunidades de pegar mal.
- **Nada de estado heredado**: si un bloque anterior definió una variable, este la vuelve a definir. Y lo que el bloque asume del entorno del operador —un PAT, un token, una var de shell— **no se asume: se verifica**, con un guard que falla diciendo qué falta.
- **Sin `$` de prompt al inicio de línea y sin la salida esperada mezclada adentro.** Ensucian el pegado.
- **Las explicaciones van afuera del bloque**, o adentro como comentarios `#`. Nunca partiendo el comando en dos para intercalar un párrafo.
- **Los placeholders son el último recurso.** Si el valor se puede resolver —un número de issue, un SHA, una ruta—, se resuelve y va literal. Cuando de verdad depende del operador, va en `MAYÚSCULAS`, uno solo por bloque idealmente, y qué poner se explica **arriba** del bloque.
- **Si el comando es destructivo, requiere `sudo` o toca algo compartido, se dice antes en una línea.** Sigue siendo pegable: se avisa, no se mutila.

```bash
cd /ruta/absoluta/al/repo && git status --short
```

### Un stack de comandos es un solo comando

El caso que más falla no es el comando suelto: es la **secuencia** —exportar credencial, cargar un `.env`, correr la herramienta—. Pegada como tres líneas sueltas tiene tres problemas que no se ven hasta que ya corrió.

Así lo entregó el harness, y no está listo para pegar:

```bash
export SUPABASE_ACCESS_TOKEN=$MI_PAT
set -a; . supabase/env/stg.env; set +a
supabase config push --project-ref <project-ref>
```

1. **Falta el `cd`.** `supabase/env/stg.env` es relativa al repo del codebase, no al vault.
2. **`$MI_PAT` se asume definida.** Si no lo está, `export` no falla: deja el token **vacío**, y el error aparece tres líneas después como "no autenticado", que manda a diagnosticar la cosa equivocada.
3. **No hay cortocircuito.** Sin `&&`, si el `.env` no existe la tercera línea corre igual — y `config push` empuja configuración incompleta a un proyecto real. El fallo silencioso es el caro.

Pegable:

```bash
( cd /ruta/absoluta/al/repo \
  && : "${MI_PAT:?definí MI_PAT en el entorno antes de correr esto}" \
  && export SUPABASE_ACCESS_TOKEN="$MI_PAT" \
  && set -a && . supabase/env/stg.env && set +a \
  && supabase config push --project-ref <project-ref> )
```

Qué agrega cada pieza:

- El **subshell** `( … )` deja la sesión del operador como estaba: no le cambia el directorio ni le deja un token exportado dando vueltas. Si el operador necesita esas variables después, se le dice y se saca el subshell.
- El **guard** `: "${VAR:?mensaje}"` corta ahí mismo con un mensaje que nombra la variable. Dentro del subshell aborta el subshell, nunca la terminal del operador.
- El **`&&` encadenado** hace que el primer error sea el último paso. `set -e` no sirve acá: en la shell interactiva del operador cierra la sesión.
- Las **comillas** en `"$MI_PAT"` — un valor con espacios o vacío rompe distinto y peor sin ellas.

**Los secretos son la única excepción a "resolvé los valores".** Un token no se pega en el chat ni se escribe en un doc: viaja como nombre de variable, con su guard. Todo lo demás —el project-ref, la ruta, el número de issue— va literal y resuelto.

### Cuándo no hace falta

Cuando el comando no es para pegar sino una **cita** —mostrar qué corriste, o qué hace un script— no lleva `cd` ni se lo trata como bloque ejecutable. Si el operador lo va a correr, es pegable; si es ilustración, decilo en la línea que lo introduce.

