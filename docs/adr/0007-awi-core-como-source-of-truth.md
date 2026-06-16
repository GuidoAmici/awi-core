# awi-core es el source of truth; la instancia es downstream

Las instancias AWI se clonaban desde `awi-core` pero evolucionaban de forma independiente — skills, hooks y settings se modificaban directamente en la instancia y luego se propagaban manualmente a awi-core. Esto produjo drift bilateral: cambios que nunca llegaron al source, y un repo separado (`GuidoAmici/my-awi-instance`) que Claude confundía con código fuente.

Decidimos invertir el flujo: todo cambio a skills, hooks y configuración del harness se hace primero en `awi-core`. La instancia es un clon que consume awi-core via submodule — nunca es la fuente. Los archivos instancia-específicos (`user-submodules.json`, `current-user.json`, datos de org y usuario) viven en submodulos separados y no forman parte de awi-core.

La alternativa era mantener la instancia como source y sincronizar hacia awi-core con un script. Se descartó porque invierte la dirección natural del control de versiones y requiere un paso manual que se saltea.

## Consecuencias

- `GuidoAmici/my-awi-instance` como repo GitHub puede eliminarse una vez que awi-core tenga todos los skills y hooks correctos.
- Los agentes que trabajen sobre el harness deben abrir PRs en `awi-core`, no en la instancia.
- El skill `awi-core-sync-status` queda obsoleto — no hay nada que sincronizar porque la instancia ya no origina cambios.
