# Delegación en dos niveles, y las preguntas con número fijo

> **Estado: aceptado (2026-10-11).** Lo pidió el operador: los tokens de Claude se
> consumían muy rápido con la forma en que se usaban las sesiones paralelas y los
> subagentes. Pidió también sumar la numeración fija de las preguntas, que el Chief of
> Staff ya venía aplicando en la práctica.

## El problema

Del 9 al 11 de octubre, el trabajo de New Haze corrió en cuatro sesiones interactivas
abiertas al mismo tiempo, durante horas:

- el Chief of Staff, que filtra lo que llega al operador;
- Nexus, que orquesta el panel interno y le delega a dos subagentes (panel y DBA);
- la sesión de los epics de la webapp;
- la sesión del panel.

Un pedido del operador cruzaba hasta cuatro contextos (CoS → Nexus → subagente del
panel → subagente DBA), y cada uno volvía a leer lo que el anterior ya sabía y lo
reescribía para el siguiente. Además:

- **Las sesiones largas encarecen cada turno.** Cada respuesta vuelve a procesar el
  historial completo de la sesión. El Chief of Staff llegó a compactarse.
- **Los mensajes entre sesiones eran informes de una o dos páginas.** Se pagan dos
  veces: al escribirlos y al leerlos. El detalle, además, ya estaba en el PR.
- **Todo corría en Opus con razonamiento alto,** también lo mecánico: buscar archivos,
  correr tests, editar YAML.
- **Cada sesión arrancaba con unos 22 KB de reglas inyectadas** más el estilo de salida
  `learning`, que agrega bloques didácticos en cada respuesta y no le sirve a una sesión
  que ejecuta.

## La decisión

### Dos niveles

| Nivel | Quién | Modelo | Vida |
|---|---|---|---|
| 1 | **Chief of Staff**: filtra, junta las decisiones del operador y despacha | Opus | Una sesión por día. Se cierra con `/wrap-session` y deja el traspaso |
| 2 | **[`trabajador`](../../.claude/agents/trabajador.md)**: una tarea (un issue, un PR) de punta a punta | Sonnet, razonamiento medio | Nace con un brief corto y muere con el PR y un informe |
| — | Búsquedas y lecturas masivas | Haiku (`Explore`) | Un solo uso |
| — | **[`revisor`](../../.claude/agents/revisor.md)**: PRs con migraciones, permisos o seguridad | Opus, razonamiento alto | Un solo uso |

- **No hay "dueños de área" que coordinan a otros.** El rol de Nexus como orquestador
  intermedio desaparece. Un trabajador no despacha trabajadores.
- **El Chief of Staff despacha a los trabajadores como subagentes en segundo plano,** con
  `isolation: "worktree"` cuando tocan código. Así el operador no abre ventanas, y cada
  trabajador arranca con un contexto chico y limpio. Despachar no necesita pedido
  explícito del operador: este ADR es la autorización.
- **Una sesión interactiva aparte se abre sólo cuando la tarea necesita al operador en
  vivo,** por ejemplo un diseño que se discute, un grill o una prueba de UX.

### Informes cortos

- **Diez líneas como máximo,** en los bloques de `answerable`. El detalle (evidencia,
  comandos, salidas) va en el PR o el issue, que quedan guardados y se leen sólo si hace
  falta.
- **Las preguntas al operador van sin numerar.** Las numera el Chief of Staff al
  juntarlas (ver abajo).

### Contexto liviano

- El estilo de salida `learning` queda apagado (`enabledPlugins` del usuario,
  2026-10-11).
- El trabajador lee lo justo: `grep` y rangos de archivo, no archivos enteros, y las
  salidas largas con `| tail`.

### Las preguntas tienen número fijo

Hasta acá, `answerable` renumeraba todos los bloques desde 1 en cada respuesta. Con un
operador que contesta mensajes viejos mientras el agente ya mandó otros nuevos, los
números dejan de coincidir. Pasó el 2026-10-11: el operador contestó «8. B» a la
pregunta que el agente había numerado 10, y hubo que deducirlo por el contenido.

**Cada pregunta recibe el próximo número libre y lo conserva hasta que se contesta.**
No se reusa, vuelve en cada turno mientras esté abierta, y la numeración sigue en la
sesión siguiente a través del traspaso. El operador contesta con el número solo. La
regla completa está en [`answerable`](../../plugins/answerable/rules/answerable.md),
sección «`E` tiene número fijo».

## Consecuencias

- **Una tarea del operador cuesta un contexto chico en vez de cuatro grandes.** El Chief
  of Staff es la única sesión con historia larga, y se renueva cada día.
- **El trabajador puede fallar por falta de contexto.** El brief tiene que traer el
  repo, el stack, el issue y los archivos, y eso es trabajo del Chief of Staff
  ([`delegacion.md`](../agents/delegacion.md)).
- **Lo que Sonnet no resuelve bien vuelve.** Un diseño difícil o una revisión de riesgo
  van a Opus por regla (el `revisor`), no por costumbre.
- **Las sesiones abiertas hoy terminan lo que tienen en curso,** y no se les asigna nada
  nuevo.
- **No se mide todavía.** El consumo por sesión se ve con `/usage`. Si en dos semanas el
  consumo no bajó, se revisa este ADR con esos números.
