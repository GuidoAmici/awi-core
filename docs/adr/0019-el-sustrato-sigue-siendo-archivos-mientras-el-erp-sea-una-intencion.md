# El sustrato sigue siendo archivos mientras el ERP sea una intención

> **Estado: aceptado (2026-08-03).**
> Este fue el único ADR de la fase 2 que un agente no podía cerrar por su cuenta: el
> insumo y la evidencia son de un agente, la decisión es del operador. Ver el PRD 5
> ([#84](https://github.com/GuidoAmici/awi-core/issues/84)).
>
> Antes de aceptarlo se volvió a correr `docs/sustrato/reproducir.py` en una sesión
> distinta de la que lo escribió: reproduce el mismo resultado —4 afirmaciones de 8,
> las mismas tres brechas de diseño— con la latencia en 65 ms contra los 54 ms de la
> corrida original, variación de medición que no cambia la conclusión. La evidencia
> es reproducible por terceros, que es la condición que el ADR 0013 pedía.

## El problema

AWI compone repositorios de git con markdown adentro. El destino que el operador
describe es otra cosa: un frontend sobre un ERP que guarda información empresarial
de varios clientes, ayuda a decidir con datos y genera solicitudes de features.

Esa diferencia se planteó como de categoría, no de escala: datos empresariales
multi-cliente necesitan control de acceso por cliente, consultas, escritura
concurrente y auditoría por registro, y se asumió que git no da ninguna de las
cuatro.

Su apertura tiene un costo hoy: bloquea dos decisiones ya tomadas y sin
implementar —la capa 3 del [ADR 0011](0011-la-composicion-es-una-capa-con-dueno.md)
y el campo `rev` del [ADR 0012](0012-contextos-flotan-dependencias-pinean.md)—
porque ambas se leyeron como apuestas a que git es el sustrato definitivo.

## La evidencia

Cada afirmación sobre lo que git no puede hacer **se reprodujo en repositorios
aislados** antes de darse por buena, con
[`docs/sustrato/reproducir.py`](../sustrato/reproducir.py). Es el criterio que el
[ADR 0013](0013-revision-integral-de-awi-core.md) identificó como faltante, y el
[ADR 0010](0010-referencias-por-nombre-no-por-version.md) es el ejemplo de qué pasa
cuando no se aplica: tres cargos contra los submódulos que resultaron ser higiene de
configuración.

**Reproducen 4 de 8 afirmaciones. Tres de las que no reproducen cambian el análisis:**

| Eje | Reproduce | Brecha |
|---|---|---|
| Control de acceso por cliente | **sí** | **diseño** — la unidad de permiso de git es el repo |
| Consulta sobre los datos | **sí** | **diseño** — indexa por ruta y hash, nunca por valor |
| Escritura concurrente sobre el mismo archivo | **sí** | **diseño**, sólo para dato estructurado |
| Trabajo sin conexión | sí, git lo da | ninguna — capacidad **a proteger** |
| Escritura concurrente en archivos distintos | **no** | ninguna |
| Auditoría por registro | **no** | ninguna, si el registro es una línea |
| Latencia de propagación | **no** | del **mecanismo**, no del sustrato |
| Invariante del ADR 0011 | **no se cae** hoy | ninguna hoy |

Lo que cada una de las tres que no reprodujeron significa:

**Auditoría por registro.** `git blame` atribuye cada línea a su autor y su commit,
y `git log -L n,n:archivo` devuelve todas las revisiones por las que pasó esa línea
con su diff. Si un registro es una línea o un archivo, la auditoría por registro
**ya existe** y es más completa que la de una tabla sin triggers: incluye el antes y
el después, no sólo el hecho del cambio. Este eje deja de ser un argumento para
migrar.

**Latencia de propagación.** El viaje completo commit → push → pull se midió en
54 ms sobre un remoto local. Lo que falta no es velocidad: es **que alguien dispare
el pull**. El requisito de tiempo real es del mecanismo de sincronización, no del
almacenamiento, y responderlo mal produce una migración innecesaria.

**El invariante del 0011.** Resolver a qué repo pertenece una ruta subiendo por sus
padres hasta encontrar `.git` funciona sin invocar git: es una propiedad del
filesystem. El invariante se sostiene, y se caería cuando un dato **deje de tener
ruta** — no cuando cambie el sustrato.

## La decisión propuesta

**Los archivos siguen siendo archivos.** La intuición del operador —*«me parece más
sencillo entenderlo como un filetree»*— sale reforzada por la evidencia, no
debilitada.

Las tres brechas de diseño que quedan comparten una condición: aparecen sobre **dato
estructurado, multi-cliente y consultable**. Mientras el ERP sea una intención y no
un sistema con datos adentro, ninguna de las tres se está pagando.

Concretamente:

1. **No se migra ahora.** Se conserva git como sustrato del contexto cualitativo
   —agenda, documentación, decisiones—, que es todo lo que hay hoy.
2. **El requisito de tiempo real se resuelve en el mecanismo**, no en el sustrato: un
   disparador de sincronización, sin mover dónde viven los datos.
3. **Cuando el ERP exista con datos reales, va a una base**, y la frontera se define
   por escrito antes de escribir una línea: qué dato vive de qué lado y **cómo se
   referencian entre sí las dos mitades**. Una frontera sin definir es la que se
   filtra, y la referencia es la parte que se rompe.

El costo de esperar es asimétrico y a favor de esperar: el sistema está en alpha con
tres usuarios, así que **el momento más barato de migrar sigue estando disponible**
mañana. Lo que no está disponible dos veces es el costo de migrar algo que todavía
no existe.

## Qué la falsaría

Nombrado por adelantado, siguiendo el patrón del ADR 0010. Cualquiera de estas
reabre la decisión:

1. **Un requisito que exija leer datos de dos clientes en la misma consulta.** El
   repo-por-cliente deja de ser una frontera y pasa a ser un obstáculo.
2. **Que un registro pase a ser una fila con muchas columnas cambiando
   independientemente.** Ahí la auditoría por línea deja de servir, y el eje que no
   reprodujo empieza a reproducir.
3. **Volumen que haga sentir el costo lineal de la consulta.** Con 200 registros son
   5 ms. Si una consulta interactiva sobre 200 mil registros aparece en un flujo
   real, la brecha de consulta pasa de teórica a bloqueante.
4. **Un requisito de control de acceso más fino que un repo entero.** Por ejemplo,
   que dentro de un cliente haya datos que un colaborador de ese cliente no pueda
   ver.
5. **Que el trabajo sin conexión deje de importar.** Es el eje que hoy pesa contra
   migrar; si deja de valer, la balanza cambia.

## Lo que esto desbloquea

### El `rev` del ADR 0012: **desbloqueado e implementado**

Se reevaluó por separado, como el PRD pedía, y **no dependía del sustrato**.
`agency-agents` es un repo de terceros en cualquier escenario —no es dato del ERP—,
y el riesgo que el `rev` cierra es de hoy: un rename upstream rompe una skill en
silencio. El PRD 3 lo agravó al hacer que `agent_personas.py` descubra personas de
ese árbol, así que un rename upstream ahora rompe el descubrimiento.

Implementado en `manifest.materialise_target()`: una entrada `system-repo` con `rev`
se materializa en ese commit o tag, y un checkout existente en otro commit reporta
**drift** en vez de corregirse en silencio — alinear es un acto deliberado, porque
corregirlo solo sería mover al operador de donde está.

La política por categoría se mantiene y hay un test que la asevera: un org
workspace es contexto compartido y **flota**, incluso si alguien le escribe un `rev`
en el manifiesto. Pinear un contexto congelaría lo que su valor exige que esté al
día.

### La capa 3 del ADR 0011: **desbloqueada, sin implementar todavía**

Su invariante se sostiene —está reproducido— así que no hay razón para archivarla.
Pero desbloquearla no es implementarla: mapa de fronteras, `status` compuesto y
ruteo de escritura son trabajo propio, y merecen su propio issue con su propio
alcance.

Lo que este ADR cierra es la **incertidumbre**: deja de estar diferida por una
pregunta abierta y pasa a estar pendiente por prioridad, que es un estado honesto.
Dejarla decidida y sin ejecutar por tiempo indefinido acumula deuda de credibilidad
en el registro, y es la condición que el ADR 0013 identificó como problemática.

## Consecuencias

- **El criterio de reversibilidad se levanta parcialmente.** La fase 1 se construyó
  sin dar esta pregunta por respondida. Con la respuesta «archivos por ahora, base
  cuando el ERP exista», se puede invertir en lo que sirve bajo cualquier sustrato
  —y consolidar duplicados byte-idénticos siempre lo fue— pero **no** en rediseñar la
  superficie de skills, que es lo que el PRD 4 dejó afuera por esta razón.
- **La pregunta queda cerrada con fundamento y no por inercia**, que es la diferencia
  que el PRD buscaba.
- El prototipo `docs/sustrato/reproducir.py` **es descartable y no lleva tests**, a
  propósito: un prototipo con tests es una implementación con otro nombre. Se
  conserva porque su valor es reproducible — cualquiera puede volver a correrlo
  cuando alguna de las cinco condiciones de falsación aparezca.
