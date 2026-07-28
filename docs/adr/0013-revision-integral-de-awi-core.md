# Revisión integral de awi-core antes de seguir construyendo

Los ADRs [0010](0010-referencias-por-nombre-no-por-version.md), [0011](0011-la-composicion-es-una-capa-con-dueno.md) y [0012](0012-contextos-flotan-dependencias-pinean.md) se escribieron el 2026-07-28 a partir de una única auditoría de arquitectura. Dejan tres decisiones tomadas y ninguna implementada. Antes de implementarlas, decidimos someter awi-core a una revisión integral de su estructura y su funcionamiento, con la pregunta abierta de si conviene **rehacerlo desde la base** usando todo lo acumulado como experiencia.

La razón para frenar acá y no seguir construyendo es que el registro de decisiones muestra un patrón, no incidentes aislados:

**El fundamento se reescribe más seguido que la decisión.** El ADR 0001 quedó supersedido por el 0009; el 0009 conserva su decisión pero el 0010 le reemplaza el fundamento entero, porque los tres cargos que lo sostenían eran higiene de configuración. Dos de trece ADRs con la razón reescrita después de los hechos sugiere que las decisiones se están tomando contra síntomas y no contra el problema de dominio.

**Las migraciones quedan a medias y dejan residuo activo.** Es el cargo que el 0010 le imputa al 0001 —no versionar gitlinks mientras se seguían usando submódulos— y se repite hoy: `.gitignore` sigue ignorando `.gitmodules` citando un script eliminado (`generate_gitmodules.py`) y un ADR supersedido, y justifica `_system/agency-agents/` con *"their gitlinks are not versioned either"* cuando ya no hay gitlinks en ninguna parte.

**El propio registro perdió disciplina.** `0005` y `0006` numeran dos decisiones distintas cada uno; `0007` y `0008` son la misma decisión duplicada en inglés y en español. El índice que debería ser la memoria del sistema tiene colisiones y duplicados.

**La capa que sostiene el invariante nunca existió.** La proyección y el gobierno de la composición (ADR 0011) no se sacaron en una migración: nunca se construyeron. El sistema viene operando sin dueño de su propia composición desde el principio.

Contra eso hay que registrar también lo que *no* es evidencia. La auditoría del 2026-07-28 citó como prueba de campo que `rabbitek` figuraba activa en el manifiesto sin existir en disco. En la instancia de referencia eso no reproduce: `plan()` resuelve nueve repos y los nueve están materializados, sin warnings. El argumento por la capa 3 se sostiene solo; su única prueba empírica, no.

## Qué se lleva la revisión como insumo

- El reencuadre del problema de dominio: componer unidades con dueños y ciclos de vida distintos en una vista coherente para un agente que opera desde la raíz. Todo lo demás es mecanismo.
- El error de categoría de fondo: pedirle a git que además de versionar, componga.
- Las tres capas del ADR 0011 y el invariante de fronteras, como criterio para juzgar cualquier diseño nuevo — no como diseño ya adoptado.
- La distinción contexto / dependencia del ADR 0012, que es anterior al mecanismo y sobrevive a cualquier rediseño.
- El test de falsación abierto del ADR 0010.
- El criterio que hizo falta y no estaba: distinguir una falla de arquitectura de una de configuración **antes** de escribir el ADR, reproduciéndola.

## Consecuencias

- Los ADRs 0011 y 0012 quedan decididos y **no** implementados. Ninguna de sus acciones —`.ignore`, `status` compuesto, campo `rev`, mapa de fronteras, ruteo de escritura— se ejecuta hasta que la revisión concluya. Implementarlas ahora es apostar a que la base sobrevive la revisión.
- El residuo de `.gitignore` se limpia dentro de la revisión, no antes: si el mecanismo cambia, el archivo cambia con él.
- La numeración y el idioma de los ADRs se resuelven en la revisión. Este ADR es el último bajo el esquema actual.
- Rehacer desde la base es una salida legítima de la revisión, no un fracaso. Los trece ADRs conservan su valor como registro de lo aprendido aunque el código que los motivó desaparezca.
- Si la revisión concluye que la base se conserva, este ADR se cierra y 0011 y 0012 se desbloquean tal como están.
