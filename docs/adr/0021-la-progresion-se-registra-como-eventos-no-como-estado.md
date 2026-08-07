# La progresión se registra como eventos, no como estado

> **Estado: aceptado (2026-08-07).**
> Insumo y análisis de un agente; la decisión es del operador. Sale de la sesión en
> que se definió que AWI debe dar dirección a los empleados según su etapa, y no
> sólo responder consultas sobre documentación.

## El problema

El operador quiere que AWI guíe a cada persona según la etapa en la que está
**dentro de cada área funcional** de la empresa, sin tener que evaluarlas él. Eso
exige que el sistema sepa en qué punto está cada persona en cada área.

La forma directa de resolverlo es un campo de estado en el perfil: `packaging:
etapa 2`, `ventas: etapa 1`, `desarrollo: etapa 3`, mutable, uno por persona.

Esa forma **reabre el [ADR 0019](0019-el-sustrato-sigue-siendo-archivos-mientras-el-erp-sea-una-intencion.md)**,
aceptado cuatro días antes, que decidió conservar archivos como sustrato mientras
el ERP fuera una intención. El 0019 nombró por adelantado cinco condiciones que lo
reabrirían, y el perfil con estado mutable activa dos:

> **2.** *"Que un registro pase a ser una fila con muchas columnas cambiando
> independientemente. Ahí la auditoría por línea deja de servir, y el eje que no
> reprodujo empieza a reproducir."*

> **4.** *"Un requisito de control de acceso más fino que un repo entero. Por
> ejemplo, que dentro de un cliente haya datos que un colaborador de ese cliente no
> pueda ver."*

Un perfil por empleado, con una columna por área, cambiando cada una por su cuenta,
es exactamente la primera. Y si hay varios empleados, es difícil que todos deban
ver las métricas de todos: es la segunda.

## La decisión

**La progresión se registra como log de eventos append-only, no como estado
mutable.** El estado —en qué etapa está alguien en un área— se **deriva** leyendo el
log, no se guarda.

Con eso ninguna de las dos condiciones se activa: no hay fila con columnas
cambiando independientemente, hay líneas que se agregan. Y el 0019 documenta que
ese es justamente el caso que git resuelve **mejor** que una tabla:

> *"Si un registro es una línea o un archivo, la auditoría por registro ya existe y
> es más completa que la de una tabla sin triggers: incluye el antes y el después,
> no sólo el hecho del cambio."*

Tres razones más, en orden de peso:

1. **Es el mecanismo que la empresa ya validó.** New Haze Learn no guarda «nivel 2»
   para un cultivador: Twick otorga XP en eventos y el nivel se infiere por
   consistencia. La progresión de empleados es el mismo sistema apuntando hacia
   adentro, y copiar un mecanismo probado cuesta menos que diseñar otro.
2. **El patrón ya existe en AWI.** `_data/users/<id>/command-log.jsonl` es un log
   append-only de una línea por evento. No hay formato nuevo que inventar.
3. **Conserva la reversibilidad.** El 0019 argumenta que el momento más barato de
   migrar sigue disponible mañana, y que lo que no está disponible dos veces es el
   costo de migrar algo que todavía no existe. Un log de eventos no gasta esa
   opción: si más adelante conviene una tabla, el log es precisamente el insumo
   para poblarla.

## Qué la falsaría

- **Que derivar el estado se vuelva caro.** Con decenas de eventos por persona,
  recorrer el log es instantáneo. Si aparece un flujo interactivo que lo recorra
  miles de veces, corresponde materializar el estado — primero como caché derivada,
  y sólo después como fuente.
- **Que haga falta corregir el pasado y no sólo agregarle.** Un log append-only
  asume que los eventos son hechos. Si aparece la necesidad de editar o borrar
  eventos de forma rutinaria —no como excepción auditada—, el modelo deja de
  encajar.
- **Que el control de acceso se vuelva un requisito real.** La condición 4 del 0019
  sigue en pie: el log evita el problema mientras los perfiles vivan en el espacio
  de cada usuario. Si la progresión tiene que ser consultable de forma central por
  un tercero que no debe ver todo, vuelve a aparecer.

## Consecuencias

- El diseño de las etapas por área queda **pendiente y es insumo del operador**: la
  forma está decidida, el contenido no. Cuáles son las etapas de cada una de las 6
  áreas funcionales, y qué evento marca el paso de una a otra, no se puede derivar
  del repositorio.
- El esquema del evento tampoco está definido acá. Como mínimo necesita persona,
  área, qué ocurrió y cuándo; si lleva algo más —quién lo observó, contra qué
  criterio— es parte del mismo trabajo pendiente.
- **No habilita por sí solo la dirección por etapa.** Saber en qué etapa está
  alguien es la mitad; la otra es que las skills lean esa etapa y cambien qué
  ofrecen. Eso es trabajo aparte y merece su propio alcance.
- El [ADR 0019](0019-el-sustrato-sigue-siendo-archivos-mientras-el-erp-sea-una-intencion.md)
  **no se reabre**. Sus cinco condiciones de falsación siguen vigentes tal como
  están escritas.
