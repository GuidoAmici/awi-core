# Las reglas de forma son un plugin y las de AWI son CLAUDE.md

> **Estado: aceptado (2026-09-04).**
> Enmienda al [ADR 0021](0021-el-operador-contesta-por-direccion-no-reescribiendo.md),
> que decidió el hook `SessionStart` y dejó `INSTRUCTIONS.md` como fuente de verdad.
> El mecanismo de las direcciones no cambia; cambia dónde vive y cómo llega.

## El problema

`INSTRUCTIONS.md` mezclaba dos cosas con audiencias distintas. Unas 255 líneas describían
**cómo se escribe una respuesta** —los cinco bloques, el TLDR, la paráfrasis del
identificador, el bloque pegable— y valen en cualquier sesión de Claude Code, con AWI o
sin AWI. Las otras 365 describían **cómo se opera AWI** y no significan nada fuera de
este árbol.

Las dos viajaban juntas por el único canal que había: un hook de `SessionStart` que hacía
`cat` del archivo entero. Eso producía dos costos simétricos. Las reglas de forma sólo
regían en el repo que tenía el hook —abrir `newhaze-webapp` era perder los cinco bloques—
y las reglas de AWI se pagaban enteras aunque la sesión no tocara el vault.

El [ADR 0021](0021-el-operador-contesta-por-direccion-no-reescribiendo.md) evaluó migrar
`INSTRUCTIONS.md` a `CLAUDE.md` y lo descartó. La razón era correcta entonces y dejó de
serlo: se descartó porque `CLAUDE.md` es específico de Claude Code y `INSTRUCTIONS.md` se
declaraba compartido entre agentes. Pero el
[ADR 0014](0014-el-problema-era-la-distribucion-no-la-composicion.md) ya había eliminado
`AGENTS.md`, `GEMINI.md` y `.gemini/` bajo el título «AWI vuelve a ser Claude-native». La
fuente de verdad se defendía como multi-agente en un sistema con un solo agente.

## Lo que cambió el diagnóstico

Un plugin de Claude Code puede empaquetar skills, comandos, agentes y **hooks**, y se
instala con versión, actualización y alcance por proyecto o por usuario. El precedente es
de Anthropic: `explanatory-output-style` y `learning-output-style` son plugins oficiales
cuyo contenido entero es un hook de `SessionStart` que inyecta un estilo de respuesta —
cada uno se describe a sí mismo como imitación de un output style que se dejó de shipear. El mecanismo de output styles sigue existiendo —`outputStyle` en `settings.json`, y Claude Code trae los suyos— pero Anthropic empaquetó éstos como plugin con hook, que es el precedente que importa acá: es la forma de distribuir un estilo propio.

Es exactamente la forma de las 255 líneas. No hacía falta inventar un mecanismo: hacía
falta darse cuenta de que el que ya se estaba usando era distribuible.

## Decisiones

**Las reglas de forma salen a un plugin, `answerable`.** Un `plugin.json`, un hook de
`SessionStart` y `rules/answerable.md`. Sin skills y sin estado: las reglas rigen desde el
primer turno o no rigen. El nombre no lleva prefijo `awi-` a propósito — su valor es que
alguien lo instale sin querer nada de AWI, y un prefijo le pone techo a esa audiencia.

**El nombre nombra la propiedad, no el diseño.** `answerable` es que la respuesta se
conteste señalando. La alternativa descriptiva —`reply-blocks`— codifica una taxonomía que
el ADR 0021 ya enmendó tres veces en tres días; un nombre que envejece con la forma es
deuda desde el día uno.

**`CLAUDE.md` pasa a ser la fuente de verdad de AWI e `INSTRUCTIONS.md` se elimina.** No
queda stub ni redirección: un archivo que sólo dice dónde está el archivo verdadero es el
residuo que el [ADR 0013](0013-revision-integral-de-awi-core.md) diagnosticó como patrón.
El hook `load-instructions.sh` y su entrada en `settings.json` se van con él.

**Lo que sólo alcanza a una rama del trabajo sale a `docs/agents/`,** que ya era la
convención del repo para eso: `contexto-compartido.md`, `docker-wsl.md`, `delegacion.md` y
`decisiones.md`. La política del tracker —cuándo preferir MCP sobre `gh`, cómo se cierra el
loop de un issue y qué issue está en juego contra qué duerme— se consolida en
`issue-tracker.md`, que ya existía.

**Lo que el entorno ya declara deja de estar escrito.** La tabla de doce herramientas de
GitHub MCP la anuncia el harness en cada sesión, y el árbol de directorios lo devuelve un
`ls`. Las dos eran cachés de una consulta barata, y una caché de eso sólo puede
desactualizarse. Se conservan el porqué y las convenciones que no se pueden mirar.

**Obsidian sale del sistema.** El operador nunca lo usó —no hay `.obsidian/` en el árbol—
y la sección «Links & Navigation» existía sólo para sus wiki-links. La convención `[[slug]]`
queda pendiente de decidir por separado: perdió su razón original pero ganó otra por el
camino, porque `grep -rl "\[\[slug\]\]"` es un índice de backlinks que no necesita lector.

## Consecuencias

- **La primera sesión después de esto pierde las reglas de forma hasta que el plugin se
  instale.** Es un corte real, de un solo comando, y el precio de no dejar las 255 líneas
  duplicadas en los dos lados durante la transición.
- `awi-core` gana un `.claude-plugin/marketplace.json` en la raíz y pasa a ser también un
  marketplace. Es aditivo: no cambia cómo se clona ni cómo se actualiza hoy.
- `init_awi.py` deja de escribir un stub de `INSTRUCTIONS.md` y genera un `CLAUDE.md`
  autosuficiente. El resto de su desactualización —scaffoldea `_clients/` y habla de
  submódulos, dos mecanismos eliminados— **es anterior a este cambio y sigue abierta**.
- Los ADRs 0014, 0020 y 0021 siguen nombrando `INSTRUCTIONS.md` y así se quedan: narran
  cuándo existía, y reescribir un ADR para que no mencione lo que había es perder el
  registro.
- La pregunta de si AWI entero se convierte en plugin **queda abierta a propósito.** Este
  ADR mueve la capa que no depende de esa respuesta; el motor sigue donde estaba.
