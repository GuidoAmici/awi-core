# Changelog

Las versiones `0.3.0` en adelante se reconstruyeron retroactivamente el 2026-07-29 a partir del historial, un hito por decisión de arquitectura registrada. Ver [ADR 0014](docs/adr/0014-el-problema-era-la-distribucion-no-la-composicion.md).

## [0.8.0](https://github.com/GuidoAmici/awi-core/compare/v0.7.0...v0.8.0) (2026-08-03)


### Características

* **delegate:** least privilege y trazabilidad en la delegación ([37264a3](https://github.com/GuidoAmici/awi-core/commit/37264a3e18c8760a9933fd781eb2b030014db421))
* **seguridad:** hook de pre-commit sobre el mismo motor de reglas ([136866f](https://github.com/GuidoAmici/awi-core/commit/136866f756562b81097c7fef8b772ef4138fb556))
* **seguridad:** motor de reglas único y auditoría del historial ([8617ef3](https://github.com/GuidoAmici/awi-core/commit/8617ef31b284476c990ad5a59ddb5b6b1237461b))
* **seguridad:** purga verificada del historial y su coordinación ([2b7dddf](https://github.com/GuidoAmici/awi-core/commit/2b7dddf6aa8257c52f7dcc87e144cee833571583))


### Correcciones

* **ci:** configurar identidad de git en el runner ([0c0a9b2](https://github.com/GuidoAmici/awi-core/commit/0c0a9b282a73eb846e4f8426b0b0397dc0ef9dda))
* **ci:** fetch-depth 0 en la promoción a main ([fba354c](https://github.com/GuidoAmici/awi-core/commit/fba354cc49ca0943454ef60a4f126418a801d68c))
* **ci:** instalar git-filter-repo en el runner ([a955be8](https://github.com/GuidoAmici/awi-core/commit/a955be8e6a43fd19234778f0a26436675486d3e8))
* **seguridad:** el inventario perdía rutas de blobs compartidos ([2be1017](https://github.com/GuidoAmici/awi-core/commit/2be10171cb3537d9bac3058b80051887c12e71fb))


### Refactorizaciones

* **skills:** consolidar el scaffolding y volver confiable la telemetría ([8ad6c84](https://github.com/GuidoAmici/awi-core/commit/8ad6c8438fb8b11e88718af9baaa99073350c65e))


### Mantenimiento

* **repo:** .mailmap para unificar las identidades de git del operador ([0b06eb6](https://github.com/GuidoAmici/awi-core/commit/0b06eb6f42d0b9298ec896784135d6f9a4049b60))


### Documentación

* **adr:** aceptar el 0019 — el sustrato sigue siendo archivos ([b3bce64](https://github.com/GuidoAmici/awi-core/commit/b3bce6492687ebdd9f2f2a0709fa5fc7f3037411))
* **changelog:** rescatar las entradas de 0.2.0 antes de eliminar stg ([2114769](https://github.com/GuidoAmici/awi-core/commit/21147692fdd0de7b35ec10a0284553a4ceb92fb3))
* **contexto:** eliminar employees.json y ordenar el registro de decisiones ([125d839](https://github.com/GuidoAmici/awi-core/commit/125d839aa06f902429c7e7af7a91e3f8a2c01a48))
* **contexto:** reescribir CONTEXT.md y el README sobre el mecanismo real ([2b7b6f2](https://github.com/GuidoAmici/awi-core/commit/2b7b6f2528604f771abdd4f8a8ff83aeba516bd0))
* **sustrato:** reproducir qué puede git y desbloquear el rev del 0012 ([e85dd24](https://github.com/GuidoAmici/awi-core/commit/e85dd249bc07fb89ceee117ea56c40ba50195275))

## [0.7.0](https://github.com/GuidoAmici/awi-core/compare/v0.6.0...v0.7.0) (2026-07-29)

La revisión integral que abría el ADR 0013, y la fase 1 completa. Reencuadra el problema de dominio —la pieza faltante era la distribución, no la composición— y construye el canal que nunca existió.

**Lo que cambia para quien opera una instancia:** `/awi-update` trae el harness sin necesidad de saber git, y el contexto compartido se sincroniza solo al abrir la sesión. `/awi-sync` ya no existe.

### Características

* `/awi-update` para que las instancias reciban el harness ([9fb94e7](https://github.com/GuidoAmici/awi-core/commit/9fb94e7))
* la rama decide la operación, no sólo el ref — reset en `main`, fast-forward en el resto ([bb4895a](https://github.com/GuidoAmici/awi-core/commit/bb4895a))
* rescatar el trabajo local en vez de destruirlo, a un stash o a una rama `respaldo/` ([273d443](https://github.com/GuidoAmici/awi-core/commit/273d443))
* reemplazar `/awi-sync` por el ciclo de contexto coordinado ([89b56af](https://github.com/GuidoAmici/awi-core/commit/89b56af))
* tope de reloj por delegate, y documentar el mecanismo real ([9f4b575](https://github.com/GuidoAmici/awi-core/commit/9f4b575))

### Correcciones

* no strippear el stdout de `git status --porcelain` ([18773f1](https://github.com/GuidoAmici/awi-core/commit/18773f1))
* ordenar la salida de error y esconder los `hint` de git ([af1970e](https://github.com/GuidoAmici/awi-core/commit/af1970e))

### Refactorizaciones

* volver a Claude-native y resolver la triplicación de skills ([e4b0307](https://github.com/GuidoAmici/awi-core/commit/e4b0307))

### Integración continua

* eliminar los dos workflows que duplican a `dev.yml` ([50610a1](https://github.com/GuidoAmici/awi-core/commit/50610a1))
* colapsar los cuatro workflows en uno solo ([5ad5fe9](https://github.com/GuidoAmici/awi-core/commit/5ad5fe9))
* promover `dev` → `main` sólo al verde ([18f8b4a](https://github.com/GuidoAmici/awi-core/commit/18f8b4a))

### Mantenimiento

* desversionar el scratch de agente y corregir el residuo del `.gitignore` ([8334bed](https://github.com/GuidoAmici/awi-core/commit/8334bed))
* reconstruir el changelog retroactivamente y fijar la versión ([70f03c8](https://github.com/GuidoAmici/awi-core/commit/70f03c8))

### Documentación

* cerrar el 0013 — el problema era la distribución, no la composición ([93b01f4](https://github.com/GuidoAmici/awi-core/commit/93b01f4))
* corregir el 0014 — el gate de tests existe y funciona ([4b29955](https://github.com/GuidoAmici/awi-core/commit/4b29955))
* enmendar el 0014 — el repo sigue público por restricción de plataforma ([0b8027c](https://github.com/GuidoAmici/awi-core/commit/0b8027c))
* ADR 0015 — dos ramas, porque el gate de distribución vive en el servidor ([18f8b4a](https://github.com/GuidoAmici/awi-core/commit/18f8b4a))
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

Release-please llegó a generar un `CHANGELOG.md` para `0.2.0` sobre la línea de `stg`, que nunca alcanzó `main` y se rescató antes de eliminar esa rama. Sus tres entradas:

* agent discovery desde `_system/agency-agents` — elimina `employees.json` y la skill `/delegate` ([99fe3dc](https://github.com/GuidoAmici/awi-core/commit/99fe3dc))
* CI con release-please como gate y promoción `dev` → `prod` ([5cdfbb4](https://github.com/GuidoAmici/awi-core/commit/5cdfbb4))
* CI de 3 ramas (`dev` → `stg` → `prod`) con release-please como gate ([c9c36c5](https://github.com/GuidoAmici/awi-core/commit/c9c36c5))

Las dos últimas describen el esquema que la revisión integral desarmó en `0.7.0`, y la primera una migración que quedó a medias: `employees.json` sigue vivo hoy, lo que motiva el [PRD #82](https://github.com/GuidoAmici/awi-core/issues/82).

El tag `v0.2.0` apunta a un merge del 2026-06-16 en la línea de `stg`, que no es ancestro de `main`. Se conserva como registro histórico; los números `0.1.0` y `0.2.0` quedan consumidos y no se reutilizan.
