# Medir antes de borrar: las skills sin uso registrado

Registro del criterio con el que se va a decidir sobre las skills que no aparecen
en la telemetría. Sale del PRD 4 ([#83](https://github.com/GuidoAmici/awi-core/issues/83)),
subissues [#101](https://github.com/GuidoAmici/awi-core/issues/101) y
[#102](https://github.com/GuidoAmici/awi-core/issues/102).

## Lo que se sabe, y lo que no

De 40 skills, **11 tenían alguna evidencia de uso** en 272 invocaciones
registradas. Las otras 29 no aparecían ni una vez.

Eso **no** prueba desuso. El registro subcontaba por construcción: `log_command`
se invocaba **por instrucción** desde 23 archivos `SKILL.md`, así que anotar una
invocación dependía de que el agente se acordara. Una skill que corrió veinte veces
sin que nadie la anotara es indistinguible de una que nunca corrió.

Y 29 skills sin una sola aparición tampoco es ruido de medición. Las dos cosas son
verdad a la vez: hay skills que sobran, y la telemetría no alcanza para decir
cuáles.

Esa imprecisión es un problema aparte del que iba a resolver: la única señal de qué
se usa era poco confiable justo cuando se la necesita para decidir qué borrar.
Borrar contra un registro que se sabe incompleto es el mismo error de decidir
contra síntomas que el [ADR 0013](adr/0013-revision-integral-de-awi-core.md)
diagnosticó.

## Lo que ya cambió

**`log_command` se movió de instrucción a código.** El hook
`.claude/hooks/log-skill-use.py` corre en `UserPromptSubmit` y registra cada
`/<skill>` que el operador escribe, sin depender de que nadie se acuerde. La razón
es la misma que la fase 1 aplicó al ciclo de contexto: *el juicio va en
instrucciones, la mecánica en código*, y registrar una invocación es mecánica.

Lo que gana en confiabilidad lo paga en alcance: ve las invocaciones del operador,
no las que un agente hace por su cuenta. Es el intercambio correcto, porque la
pregunta a contestar es «qué skills usa el operador».

Cada entrada lleva ahora un campo `fuente` —`prompt` para el hook, `skill` para lo
que una skill anota— y eso es lo que va a permitir medir **cuánto** subcontaba el
registro anterior: comparar las dos series sobre el mismo período.

Las invocaciones desde `SKILL.md` **se conservan**: agregan el resultado
(`completed`, `skipped`, `errored`), que el hook no puede saber. Es información que
mejora el registro si está y que si falta no lo invalida.

```bash
# qué se usó y cuántas veces
python3 .claude/skills/shared/scripts/log_command.py --conteo
```

## El criterio de decisión

**Ninguna skill se retira antes de que la medición confiable cubra un período de
uso normal.** Concretamente, antes de decidir hacen falta las tres cosas:

1. **Al menos 30 días** de registro escrito desde el hook, para que un ritual
   mensual —`/quarter`, `/year`— tenga la oportunidad de aparecer.
2. **Al menos un ciclo completo** de los rituales que existen: un cierre de
   semana, un cierre de mes.
3. **La comparación entre fuentes** hecha: cuántas invocaciones registró el hook
   contra cuántas registraron las skills, para poner número al subconteo del
   registro anterior.

Con eso, una skill se propone para retiro si **no aparece ni una vez** en el
período **y** su función está cubierta por otra que sí aparece. La segunda
condición no es opcional: una skill que no se usó pero es la única forma de hacer
algo necesario no se retira, se documenta.

## Cómo se retira

**Archivar, no borrar.** Sale del árbol y queda en el historial, y el commit que la
retira **lista cuáles fueron y cómo recuperarlas** — el mismo patrón que la fase 1
usó al eliminar `.agents/`, donde el mensaje de commit enumera las doce skills que
vivían sólo ahí.

**Toda skill retirada deja sus referencias resueltas.** Es la condición que
convierte una limpieza en algo distinto de una nueva instancia del patrón de
residuo que el ADR 0013 diagnosticó. En este PRD se aplicó al retirar
`awi-client`, `new-client` e `initialize`: sus siete referencias en el README, en
`init_awi.py` y en el ADR 0011 se reapuntaron a `/awi-org` en el mismo commit.

**Cada skill que se conserva tiene una razón registrada.** «Por las dudas» no es
una razón: es la ausencia de una.

## Qué ya se retiró, con evidencia distinta

Tres de las cuatro skills de scaffolding se retiraron **sin esperar la medición**,
porque ahí la evidencia no era estadística: `init_org.py` ≡ `init_client.py` byte a
byte, `import_client.py` duplicado, y los tres `toggle_client.py` consultaban un
registro que el [ADR 0009](adr/0009-manifiestos-json-en-lugar-de-submodulos.md)
eliminó, así que su función era leer algo inexistente.

Reducir cuatro copias idénticas a una es seguro bajo cualquier sustrato, y arreglar
un script que consulta un registro inexistente no necesita datos de uso: no
funcionaba.

| Retirada | Reemplazo |
|---|---|
| `/awi-client` | `/awi-org` — el mismo scaffolding con otro nombre |
| `/new-client` | `/awi-org` |
| `/initialize` | `/awi-org` |
| `toggle_client.py` ×3 | `.claude/skills/shared/scripts/toggle_repo.py` |
| `init_client.py`, `init_org.py`, `init_workspace.py` | `.claude/skills/shared/scripts/scaffold.py` |

**Organización y cliente son la misma cosa.** El PRD pedía determinarlo antes de
unificar, porque el vocabulario del dominio los distinguía. No los distingue:
`CONTEXT.md` define **Org Workspace** y no define «cliente» como término aparte, y
`_data/entities/` —la ruta que usaba la versión «cliente»— ya no existe. Los
scripts idénticos no eran el bug: eran la evidencia.

## Lo que queda afuera a propósito

Rediseñar qué skills debería tener AWI. Este trabajo consolida lo que hay y mide;
no propone un catálogo nuevo. Y hay una razón para no adelantarse: el
[PRD 5](https://github.com/GuidoAmici/awi-core/issues/84) puede cambiar el
sustrato, y un cambio de sustrato afectaría a las skills. Consolidar duplicados
byte-idénticos es seguro bajo cualquier sustrato; rediseñar la superficie no lo es.
