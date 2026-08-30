# El operador contesta por dirección, no reescribiendo

> **Estado: aceptado (2026-08-28), enmendado tres veces (2026-08-29, 2026-08-30).**
> Las direcciones siguen siendo el mecanismo; cambió el corte de los bloques y después
> la forma del ítem. Ver [La primera taxonomía duró un día](#la-primera-taxonomía-duró-un-día),
> [Los hilos abiertos son un bloque, no una nota al pie](#los-hilos-abiertos-son-un-bloque-no-una-nota-al-pie)
> y [El ítem también tiene TLDR](#el-ítem-también-tiene-tldr).

El harness ya tenía tres reglas sobre cómo se escribe una respuesta: el TLDR abre
diciendo de qué va, ningún identificador viaja desnudo, y un comando dirigido al
operador se pega y corre. Ninguna decía nada sobre **la forma** de la respuesta.

El resultado se veía en cada sesión. El agente contestaba una pregunta, reportaba lo
que había hecho, proponía tres mejoras y pedía una decisión — todo en la misma
prosa corrida. La respuesta tenía lo que el operador necesitaba y no le decía dónde
estaba nada: el resultado del pedido a mitad de un párrafo, la sugerencia que había
que aprobar entre dos hallazgos. Para aceptar una sola de las tres propuestas, el
operador tenía que reescribirla — o decir "la segunda" y esperar que el agente
contara igual que él.

El pedido original era ordenar los bloques. La forma que faltaba apareció al
discutirlo: **si cada ítem lleva una etiqueta estable, el operador contesta con la
etiqueta.** "`C3`, aplicalo, el resto no" es una respuesta completa, y cuesta cuatro
palabras. Las letras no son decoración tipográfica ni jerarquía visual: son
direcciones, y una dirección sólo sirve si significa lo mismo en todos los turnos.

## Decisión

**Toda respuesta al operador se estructura en cinco bloques, y cada ítem lleva su
dirección.**

| Letra | Bloque | Qué va adentro |
|---|---|---|
| `A` | Qué hice | Lo que creé, modifiqué o borré, y dónde |
| `B` | Qué tenés que saber | Lo que averigüé o detecté y el operador no sabía |
| `C` | Hilos abiertos | Lo que esta sesión empezó y no terminó |
| `D` | Qué propongo | Lo que el agente podría hacer después y no empezó |
| `E` | Qué necesito de vos | Lo que el agente no puede resolver solo |

*(Tabla enmendada dos veces el 2026-08-29. Las versiones anteriores están en las dos
secciones de enmienda, al final.)*

Lo que hace que la dirección funcione, y que se decidió pieza por pieza:

- **La letra pertenece al bloque, no al lugar.** Las propuestas son `D` aunque falten
  `A`, `B` y `C`. La alternativa —letras corridas por orden de aparición— se descartó porque
  hace que `C` signifique cosas distintas según el turno, que es exactamente lo que
  una dirección no puede hacer.
- **El tag va en el ítem, no en el título.** El bloque se titula `## Qué propongo`
  y sus ítems son `D1`, `D2`. Repetir la letra en el encabezado no agrega nada.
- **Cada ítem abre con su TLDR en negrita.** Ver la tercera enmienda.
- **Los cinco bloques numeran sus ítems**, `B` incluido: un hallazgo que no se puede
  citar no se puede objetar.
- **Sin tope de ítems.** Se evaluó un tope de tres con excedente contado, como en la
  regla de backlog. Se descartó para el bloque de decisiones: posponer un bloqueo
  para que entrara en un número es peor que una lista larga. Sin tope ahí, un tope
  en las propuestas sólo era asimetría sin ganancia.
- **Lo que contesta la pregunta va primero dentro de su bloque.** Es una regla de
  orden, no un bloque: ver la enmienda.
- **Propuesta y decisión se separan por una sola pregunta** — *¿puedo avanzar sin la
  respuesta?* Binaria, y se evalúa al escribir el ítem.
- **Los bloques vacíos se omiten, menos el último**, que se declara vacío. Es la misma
  razón por la que la línea 2 del TLDR nunca se borra: "no necesito nada de vos" es
  información.
- **Con una decisión abierta el agente no espera.** Hace todo lo que no dependa de la
  respuesta y frena sólo lo que sí.

**El TLDR se repliega a los textos escritos.** Su `Dónde aplica` nombraba las
respuestas al operador; ahora la frontera es "¿es un turno o es un documento?". Los
turnos —respuestas al operador, informe final de un subagente— usan los cinco
bloques; los documentos —issues, PRs, ADR, outputs, PRD, artifacts, briefs— siguen
abriendo con TLDR. Encimar los dos duplicaba la apertura: `A1` y `B1` ya dicen de
qué va.

## Una regla que no se carga no se cumple

La segunda mitad de la decisión no es sobre la regla sino sobre cuándo llega.

`CLAUDE.md` mandaba leer `INSTRUCTIONS.md` "antes de cualquier operación del vault".
Las reglas de escritura no esperan a una operación del vault: rigen desde el primer
turno, y en las sesiones que nunca tocan el vault —trabajo sobre un codebase, una
consulta suelta— el archivo no se abría nunca. La regla existía y no estaba en
vigor. Es el mismo modo de falla que documentó el
[ADR 0020](0020-el-ciclo-de-contexto-se-ancla-en-las-skills.md), sobre otra cosa.

**Un hook `SessionStart` inyecta `INSTRUCTIONS.md` entero al abrir la sesión**
(`.claude/hooks/load-instructions.sh`). El archivo completo y no un tramo: extraer
por secciones se desincroniza en silencio, y el modo de falla es no enterarse. Si el
archivo no está, el hook sale sin ruido — romper el arranque de la sesión es peor
que no cargar las reglas.

La alternativa que se evaluó y se descartó fue **migrar `INSTRUCTIONS.md` entero
adentro de `CLAUDE.md`**. Resolvía la carga, pero pagaba caro: quince archivos vivos
lo nombran por ruta —entre ellos `init_awi.py`, que lo escribe al scaffoldear una
instancia nueva—, y `CLAUDE.md` es específico de Claude Code, así que la promesa de
"fuente de verdad compartida entre todos los agentes" quedaba cancelada. El hook
resuelve el mismo problema sin tocar ninguna referencia.

## La primera taxonomía duró un día

La versión aceptada el 2026-08-28 cortaba los bloques así:

| Letra | Bloque | Qué va adentro |
|---|---|---|
| `A` | Lo que preguntaste | Una entrada por pregunta |
| `B` | Dónde estamos | Qué quedó hecho, después qué se encontró |
| `C` | Lo que sugiero | Lo que el agente propone y podría hacer después |
| `D` | Qué necesito de vos | Lo que el agente no puede resolver solo |

Al usarla, el operador reportó que "funcionaba algo extraño". El diagnóstico:
**los cuatro bloques no compartían un eje de clasificación.**

- **`A` cortaba transversal a los otros tres.** "Lo que preguntaste" clasificaba por
  *a quién le responde el contenido*; `B`, `C` y `D` clasificaban por *qué tipo de
  cosa es el contenido*. Entonces toda respuesta a una pregunta caía en dos bloques
  a la vez: "¿quedó hecho X?" era `A` y era `B`; "¿te parece Y?" era `A` y era `C`.
  El ruteo quedaba a criterio del turno, y el modo de falla típico era duplicar —
  contestar corto en `A` y volver a contarlo en `B`.
- **`B` eran dos bloques con un punto y coma.** Su propia definición lo confesaba:
  "qué quedó hecho y dónde; **después**, qué se encontró". Y son cosas de naturaleza
  opuesta: lo que hice es reversible y se verifica en el repo; lo que averigüé no se
  revierte y no se verifica igual.

La taxonomía nueva usa un eje único: **qué cambió el mundo / qué cambió lo que sabés
/ qué podría hacer / qué no puedo hacer solo.** `A` y `B` son pasado cerrado, `C` y
`D` futuro abierto; de lo abierto, `C` lo cierra el agente y `D` sólo el operador.
Cada frontera es binaria: `A` o `B` se decide con *¿quedó algo distinto en disco, en
el repo o en un issue?*, y `C` o `D` con la pregunta que ya estaba.

**Lo que `A` aportaba y había que reponer:** era lo único que obligaba al agente a
contestar la pregunta literal. Se repone como regla de orden y no como bloque —
*si el operador preguntó algo, lo que lo contesta es el primer ítem de su bloque*—
porque un bloque por destinatario es justamente lo que rompía el eje.

**`D` conserva su nombre, "Qué necesito de vos", y no pasó a "Qué necesito saber".**
Conformidad y aprobación no son saber: el bloque cubre decisiones, visto bueno e
información que sólo el operador tiene, y el nombre tiene que cubrir las tres.

Esto se enmendó en su lugar y no se abrió un ADR nuevo: la decisión que este
documento defiende —que el operador conteste por dirección en vez de reescribir— se
sostiene intacta. Lo que falló fue el corte de los bloques, no el mecanismo.

## Los hilos abiertos son un bloque, no una nota al pie

Un día después de la primera enmienda, el operador nombró el modo de falla que
quedaba: **abre en una sesión más cosas de las que puede cerrar, y sin un listado le
cuesta repartir el resto entre handoffs.**

El trabajo a medias no tenía lugar canónico. Se dispersaba en tres: lo empezado
aparecía en `Qué hice` con una aclaración de que había quedado corto, lo pendiente
volvía disfrazado de propuesta, y lo frenado sólo existía adentro del bloque de
decisiones. Ninguno de los tres es una lista de deuda, y el eje tenía un agujero
declarado — `A` cubría "cambió el mundo y terminó" sin que nada cubriera "cambió el
mundo y no terminó".

**Se agrega `Hilos abiertos` como tercer bloque**, entre los hechos y las propuestas.
El eje se reformula como **grado de cierre**: cerrado (`A`, `B`), abierto y empezado
(`C`), abierto y sin empezar (`D`, `E`).

- **Va antes de las propuestas, no al final.** Un hilo es pasado, y todo el pasado se
  lee junto. Puesto después del bloque de decisiones habría competido por atención
  justamente con lo que lo desbloquea.
- **`C` es el único bloque que no se renumera desde cero.** Los otros cuatro valen
  para el último turno; los hilos son de la sesión entera y persisten hasta cerrarse.
  Sin esa persistencia el bloque no sirve para lo que se pidió: en una sesión larga,
  los hilos del principio ya no están en contexto para reconstruirlos al final.
- **Sale de la lista de tres maneras**: se cierra y pasa a `A`, se abandona con
  confirmación del operador, o **se convierte en issue**. La tercera es la que reparte
  trabajo entre sesiones, y hace del bloque la bandeja de entrada de los handoffs.
- **El hilo dice dónde quedó, no qué se pensaba hacer.** Un estado retomable, no una
  intención.

Ya existía un consumidor: el `Step 1` de `/wrap-session` es un «gate de hilos
abiertos» que barre la conversación entera al cerrar para reconstruir esta misma
lista. Mantenerla turno a turno convierte ese barrido en una verificación. El
vocabulario tampoco es nuevo — la skill ya llamaba "hilos abiertos" a esto.

**El costo aceptado: `D` cambia de significado**, de "qué necesito de vos" a "qué
propongo", y aparece una `E`. Es la colisión más cara posible, porque `D` es la letra
que el operador más usa para responder. Se aceptó igual: la taxonomía tenía dos días
de uso, y la alternativa —darle al bloque nuevo una letra fuera de secuencia— rompía
que el orden alfabético sea el orden de lectura, que es una ayuda gratis. La regla de
que el agente confirma antes de actuar sobre una dirección de un turno anterior cubre
el resto.

## El ítem también tiene TLDR

La estructura resolvió *dónde* está cada cosa y no dijo nada sobre *cómo se escribe
cada ítem*. Con los bloques ya en uso, el operador señaló el hueco: un ítem que abre
con «La tercera vía de salida es la que resuelve tu problema literal» **lo obliga a
leer el párrafo entero para saber de qué se hablaba** — y a veces ni así. La
dirección lo dejaba contestar sin reescribir, pero no lo dejaba decidir sin leer
todo.

Es el mismo modo de falla que ataca la regla del TLDR, una escala más abajo: del
texto al ítem. Y es un modo de falla propio de la prosa de agente, que tiende al
teaser porque suena a que está construyendo un argumento.

**Cada ítem abre con un TLDR en negrita seguido de dos puntos**, y el resto es
evidencia. El criterio que lo gobierna: *leer sólo las negritas de una respuesta
tiene que alcanzar para tenerla entera.*

Lo que hace falta para que eso se cumpla, y que sin nombrarlo no se cumple:

- **El TLDR afirma, no anuncia.** Si admite un "Sobre" adelante y suena a título de
  sección, es un rótulo. El test es mecánico y se corre al releer.
- **Test del borrado**: tapado el detalle, el TLDR tiene que seguir siendo verdadero y
  útil solo. Si no, es un anzuelo.
- **Nombrá la cosa, no su categoría** — el dato concreto entra en el TLDR, no espera
  en el detalle.
- **Sin pronombres de suspenso** ("esto", "la clave acá", "lo que resuelve el
  problema"). Es la forma más común del acertijo.
- **Una sola negrita por ítem.** Si el detalle también resalta, no queda nada que
  escanear — y el formato entero existe para poder escanear.
- **El detalle es opcional.** Un ítem de una oración es todo TLDR y no lleva negrita.

No aplica a documentos: ahí ya manda el TLDR de cuatro líneas, y encimar los dos
duplicaría la apertura. Esta regla vive en los turnos, igual que los cinco bloques.

## Qué no cambia

- **Las otras tres reglas de escritura.** Ningún identificador viaja desnudo y los
  comandos se pegan y corren, adentro de los bloques igual que afuera.
- **Dónde vive la fuente de verdad.** `INSTRUCTIONS.md` sigue donde estaba y sigue
  siendo el único lugar donde se edita la política.
- **El piso.** Una confirmación o una respuesta de una línea no se estructura: ahí el
  mensaje entero es un solo ítem y no necesita rótulo.

## Cómo se verifica

```bash
cd /home/unixadmin/GitHub/GuidoAmici/my-awi-instance && CLAUDE_PROJECT_DIR="$PWD" bash .claude/hooks/load-instructions.sh | head -1
```

Si eso no imprime la línea de encabezado de las reglas, el hook no está cargando y
la regla vuelve a depender de que alguien se acuerde de leer el archivo.

La otra comprobación la hace el operador y no necesita herramienta: si una respuesta
de más de un párrafo no le permite contestar con una dirección, la regla no se
cumplió.
