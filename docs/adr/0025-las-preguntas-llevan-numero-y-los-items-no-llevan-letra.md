# Las preguntas llevan número y los ítems no llevan letra

> **Estado: aceptado (2026-10-16).** Lo pidió el operador. Reemplaza en parte al
> [ADR 0021](0021-el-operador-contesta-por-direccion-no-reescribiendo.md): los cinco
> bloques siguen, las direcciones con letra (`A1`, `D3`) se van. Suma también que todo
> identificador vaya enlazado.

## El problema

El [ADR 0021](0021-el-operador-contesta-por-direccion-no-reescribiendo.md) le dio a cada ítem una dirección con letra y número (`A1`, `B2`, `D3`) para que el operador pudiera contestar señalando. En la práctica, del 13 al 16 de octubre, el Chief of Staff escribió los bloques con encabezado y viñetas sin letras, y sólo las preguntas llevaron número fijo ([ADR 0024](0024-delegacion-en-dos-niveles-y-preguntas-con-numero-fijo.md)). El operador contestó siempre por número de pregunta («191. A») y nunca por la dirección de un hallazgo o una propuesta.

Al cerrar la sesión lo dijo explícito: la forma sin letras «es más apacible a la vista, minimalista y más fácil de responder». Pidió además que los números de issues, PRs y commits vengan siempre con su link.

## Decisión

1. **Los cinco bloques se quedan, con su encabezado `##`.** El eje del grado de cierre y las fronteras entre bloques no cambian.
2. **Los ítems son viñetas que abren con su TLDR en negrita, sin letra ni número.** Un hallazgo, una propuesta o un hilo se citan por su tema en pocas palabras.
3. **El número queda para las preguntas de «Qué necesito de vos»,** con la regla del número fijo del ADR 0024. Es la única referencia que el operador usa para contestar, y la que el resto de la respuesta usa para citar una decisión pendiente («frenado por la 191»).
4. **Todo identificador que trae el agente va enlazado** —issue, PR, commit, corrida de CI, ADR— además de parafraseado. El agente arma la URL.

## Consecuencias

- Una propuesta que el operador quiere aprobar o rechazar con una palabra tiene que ser una pregunta con número. Si el agente puede avanzar sin la respuesta, sigue siendo una propuesta y se cita por tema.
- El ritual de cierre de sesión toma los hilos del bloque «Hilos abiertos» por su texto, no por su dirección.
- `plugins/answerable/rules/answerable.md`, su README y las descripciones del plugin se actualizan en el mismo commit.
