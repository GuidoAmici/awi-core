# Changelog

Las versiones `0.3.0` en adelante se reconstruyeron retroactivamente el 2026-07-29 a partir del historial, un hito por decisión de arquitectura registrada. Ver [ADR 0014](docs/adr/0014-el-problema-era-la-distribucion-no-la-composicion.md).

## [0.7.0](https://github.com/GuidoAmici/awi-core/compare/v0.6.0...v0.7.0) (2026-07-29)

La revisión integral que abría el ADR 0013. Reencuadra el problema de dominio —la pieza faltante era la distribución, no la composición— y ejecuta la limpieza que no dependía de decidir el sustrato.

### Refactorizaciones

* volver a Claude-native y resolver la triplicación de skills ([e4b0307](https://github.com/GuidoAmici/awi-core/commit/e4b0307))

### Integración continua

* eliminar los dos workflows que duplican a `dev.yml` ([50610a1](https://github.com/GuidoAmici/awi-core/commit/50610a1))

### Mantenimiento

* desversionar el scratch de agente y corregir el residuo del `.gitignore` ([8334bed](https://github.com/GuidoAmici/awi-core/commit/8334bed))

### Documentación

* cerrar el 0013 — el problema era la distribución, no la composición ([93b01f4](https://github.com/GuidoAmici/awi-core/commit/93b01f4))
* corregir el 0014 — el gate de tests existe y funciona ([4b29955](https://github.com/GuidoAmici/awi-core/commit/4b29955))
* reapuntar `/grill-me` al plugin en `bdr-template` ([634da2a](https://github.com/GuidoAmici/awi-core/commit/634da2a))

## [0.6.0](https://github.com/GuidoAmici/awi-core/compare/v0.5.0...v0.6.0) (2026-07-28)

Una sola capa para traer issues, y la enmienda al fundamento del ADR 0009.

### Características

* `fetch_issues.py` como capa única de issue fetching ([a6dada0](https://github.com/GuidoAmici/awi-core/commit/a6dada0))

### Mantenimiento

* eliminar `collaborator` y `awi_upstream_branch`, y documentar `day_start_hour` ([283128e](https://github.com/GuidoAmici/awi-core/commit/283128e))

### Documentación

* enmendar el fundamento del 0009 y registrar la revisión integral ([f98a78b](https://github.com/GuidoAmici/awi-core/commit/f98a78b))

## [0.5.0](https://github.com/GuidoAmici/awi-core/compare/v0.4.0...v0.5.0) (2026-07-27)

Los manifiestos JSON reemplazan a los submódulos ([ADR 0009](docs/adr/0009-manifiestos-json-en-lugar-de-submodulos.md)). Cambia el mecanismo de composición completo: nada en AWI es un submódulo, todo se materializa por `git clone`.

### Características

* soportar el campo `type` y la elección de codebases por operador ([551dcb6](https://github.com/GuidoAmici/awi-core/commit/551dcb6))

### Refactorizaciones

* reemplazar los submódulos por manifiestos JSON y clones ([16dc8d5](https://github.com/GuidoAmici/awi-core/commit/16dc8d5))
* descubrir por manifiestos y eliminar el mirror muerto a awi-core ([ba2323c](https://github.com/GuidoAmici/awi-core/commit/ba2323c))

## [0.4.0](https://github.com/GuidoAmici/awi-core/compare/v0.3.0...v0.4.0) (2026-07-27)

awi-core pasa a ser el source of truth ([ADR 0007](docs/adr/0007-awi-core-como-source-of-truth.md)). La instancia deja de ser un repo aparte que espeja y se convierte en un checkout de awi-core.

### Correcciones

* eliminar los restos de auto-commit y las instrucciones que lo asumían ([ab13552](https://github.com/GuidoAmici/awi-core/commit/ab13552))

### Mantenimiento

* eliminar el mecanismo de mirror instancia → awi-core ([b5af8df](https://github.com/GuidoAmici/awi-core/commit/b5af8df))
* dejar de versionar `.gitmodules` y el gitlink de agency-agents ([142ccf5](https://github.com/GuidoAmici/awi-core/commit/142ccf5))
* eliminar los diagramas de workflow ([31590d5](https://github.com/GuidoAmici/awi-core/commit/31590d5))

### Documentación

* guía para migrar instancias legacy a awi-core ([daa8465](https://github.com/GuidoAmici/awi-core/commit/daa8465))
* reescribir `public-private-split` para el modelo de un solo repo ([34c0b68](https://github.com/GuidoAmici/awi-core/commit/34c0b68))
* consolidar el árbol duplicado de agentic-workflow-integrator ([5669d02](https://github.com/GuidoAmici/awi-core/commit/5669d02))
* fijar que el brief aporta el stack al delegar subagentes ([781a7da](https://github.com/GuidoAmici/awi-core/commit/781a7da))
* exigir comentar y ofrecer el cierre de issues resueltos ([f72e036](https://github.com/GuidoAmici/awi-core/commit/f72e036))
* el agente sugiere la disposición del issue, no sólo la ofrece ([199bae5](https://github.com/GuidoAmici/awi-core/commit/199bae5))

## [0.3.0](https://github.com/GuidoAmici/awi-core/compare/v0.2.0...v0.3.0) (2026-07-19)

Primera versión bajo Conventional Commits. Arranca el trabajo deliberado sobre el harness, después de la era del vault.

### Correcciones

* registrar agency-agents como submodule real ([ca14d4e](https://github.com/GuidoAmici/awi-core/commit/ca14d4e))

### Documentación

* corregir convención de issue tracker ([6ec0184](https://github.com/GuidoAmici/awi-core/commit/6ec0184))

## 0.1.0 – 0.2.0 (2026-04-11 – 2026-06-21)

La era del vault, anterior a Conventional Commits: **207 commits** con prefijo `cos:`, generados por el hook de auto-commit del chief-of-staff. No se reconstruyen entrada por entrada porque los mensajes son de operación de vault, no de cambios de harness — mayormente `cos: sync` y capturas de agenda.

Lo que se construyó en ese período: el árbol de `_system/`, las skills de rituales (`/today`, `/week`, `/quarter`, `/year`), el sistema de delegación, los hooks, y el andamiaje de orgs y usuarios.

El tag `v0.2.0` existe en el remoto apuntando a un merge del 2026-06-16 en la línea de `stg`, que no es ancestro de `main`. Se conserva como registro histórico; los números `0.1.0` y `0.2.0` quedan consumidos y no se reutilizan.
