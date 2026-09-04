# Changelog

Las versiones `0.3.0` en adelante se reconstruyeron retroactivamente el 2026-07-29 a partir del historial, un hito por decisión de arquitectura registrada. Ver [ADR 0014](docs/adr/0014-el-problema-era-la-distribucion-no-la-composicion.md).

## [0.8.0](https://github.com/GuidoAmici/awi-core/compare/v0.7.0...v0.8.0) (2026-09-04)


### Características

* **awi:** worktree por sesión — mecanismo y guard, no sólo doc ([0405291](https://github.com/GuidoAmici/awi-core/commit/04052915bb3e42a2a58520722287e898734a3f5e))
* **awi:** wrap-session levanta el bloque C en vez de reconstruirlo ([5339dcb](https://github.com/GuidoAmici/awi-core/commit/5339dcb4908ae7b05d713b997e0ebe50c5251c2c))
* **delegate:** least privilege y trazabilidad en la delegación ([37264a3](https://github.com/GuidoAmici/awi-core/commit/37264a3e18c8760a9933fd781eb2b030014db421))
* **seguridad:** hook de pre-commit sobre el mismo motor de reglas ([136866f](https://github.com/GuidoAmici/awi-core/commit/136866f756562b81097c7fef8b772ef4138fb556))
* **seguridad:** motor de reglas único y auditoría del historial ([8617ef3](https://github.com/GuidoAmici/awi-core/commit/8617ef31b284476c990ad5a59ddb5b6b1237461b))
* **seguridad:** purga verificada del historial y su coordinación ([2b7dddf](https://github.com/GuidoAmici/awi-core/commit/2b7dddf6aa8257c52f7dcc87e144cee833571583))
* **sync:** anclar el ciclo de contexto en las skills que lo abren ([ec6c59b](https://github.com/GuidoAmici/awi-core/commit/ec6c59bc64eaa38f493fd3317142c4c4e952a9df))
* **sync:** sacar los codebases del ciclo automático ([cf6ed40](https://github.com/GuidoAmici/awi-core/commit/cf6ed402c66fbc22ed1a201d711a77b452fe2e9b))
* **triage:** un issue con PR abierto no se vuelve a delegar ([80a5bc6](https://github.com/GuidoAmici/awi-core/commit/80a5bc69d8a0d0682e0393fb2840843e4704bdda))


### Correcciones

* **ci:** configurar identidad de git en el runner ([0c0a9b2](https://github.com/GuidoAmici/awi-core/commit/0c0a9b282a73eb846e4f8426b0b0397dc0ef9dda))
* **ci:** fetch-depth 0 en la promoción a main ([fba354c](https://github.com/GuidoAmici/awi-core/commit/fba354cc49ca0943454ef60a4f126418a801d68c))
* **ci:** instalar git-filter-repo en el runner ([a955be8](https://github.com/GuidoAmici/awi-core/commit/a955be8e6a43fd19234778f0a26436675486d3e8))
* **seguridad:** el inventario perdía rutas de blobs compartidos ([2be1017](https://github.com/GuidoAmici/awi-core/commit/2be10171cb3537d9bac3058b80051887c12e71fb))
* **sync:** no publicar desde una rama que no es la del manifiesto ([3ca742f](https://github.com/GuidoAmici/awi-core/commit/3ca742f18934c7d0899d5cf5319574379d2c4f18))
* **triage:** mergear no es publicar — falta el estado en-stg ([5853872](https://github.com/GuidoAmici/awi-core/commit/5853872fe3bc74c7dedec84e33f77e62df5b8207))


### Refactorizaciones

* **skills:** consolidar el scaffolding y volver confiable la telemetría ([8ad6c84](https://github.com/GuidoAmici/awi-core/commit/8ad6c8438fb8b11e88718af9baaa99073350c65e))


### Mantenimiento

* **repo:** .mailmap para unificar las identidades de git del operador ([0b06eb6](https://github.com/GuidoAmici/awi-core/commit/0b06eb6f42d0b9298ec896784135d6f9a4049b60))
* **sustrato:** registrar la corrida de reproducción del ADR 0019 ([7867a5b](https://github.com/GuidoAmici/awi-core/commit/7867a5b8d8507dcfa66dd471d787ee5373be48f6))


### Documentación

* **adr:** 0021 — la progresión se registra como eventos, no como estado ([d0f96fd](https://github.com/GuidoAmici/awi-core/commit/d0f96fd57ad73d679579023753d3866669f859f4))
* **adr:** aceptar el 0019 — el sustrato sigue siendo archivos ([b3bce64](https://github.com/GuidoAmici/awi-core/commit/b3bce6492687ebdd9f2f2a0709fa5fc7f3037411))
* **adr:** retirar el 0021 — la progresión como eventos ([9e4d23e](https://github.com/GuidoAmici/awi-core/commit/9e4d23e64706f6f0ff268f8df65245ffdb61c976))
* **afin:** documentar la adopción del ciclo en-pr/en-stg/en-prod ([31b163c](https://github.com/GuidoAmici/awi-core/commit/31b163c812ecdf0b8b00ebab14810e520de77302))
* **awi:** adoptar Strix para pentesting con IA ([5bea945](https://github.com/GuidoAmici/awi-core/commit/5bea94535581ab92e41fc3c7c93d3074dfaf1ccc))
* **awi:** cada ítem abre con su TLDR en negrita ([10591a5](https://github.com/GuidoAmici/awi-core/commit/10591a534fc7d0869878e097a807ef21c24566ab))
* **awi:** derivar qué está en juego, en vez de esperarlo del tracker ([97486c0](https://github.com/GuidoAmici/awi-core/commit/97486c0d95a9a2e185df6b3788617bcfaa754449))
* **awi:** documentar el protocolo de trazabilidad Artifact ↔ repo ([b80ee59](https://github.com/GuidoAmici/awi-core/commit/b80ee59b4baea364da435f24c0a0b61a265f1fdc))
* **awi:** el stack de comandos es lo que rompe, no el cd suelto ([6772453](https://github.com/GuidoAmici/awi-core/commit/67724530643f2bd255c1ac3ee90bb8a2f389eb0e))
* **awi:** el TLDR va primero ([a36f5a5](https://github.com/GuidoAmici/awi-core/commit/a36f5a5699296e341abd6512d8374ce0d4c80121))
* **awi:** en repos de cliente el commit lleva la identidad del repo ([54e31e8](https://github.com/GuidoAmici/awi-core/commit/54e31e83b15cbbfe7d0b2cc433a631c4670e4bec))
* **awi:** la forma de un artifact la pone el Design System de la org ([bc3dfbc](https://github.com/GuidoAmici/awi-core/commit/bc3dfbc4ff779787a82c9efa500bf807b0d1c399))
* **awi:** la respuesta al operador pasa a ser direccionable ([56136c3](https://github.com/GuidoAmici/awi-core/commit/56136c3529624cd3cffde6fc2952179e9cae9d73))
* **awi:** los cuatro bloques pasan a compartir un eje ([558c796](https://github.com/GuidoAmici/awi-core/commit/558c79622e078d5456a34f19d9bae65dd2901631))
* **awi:** los hilos abiertos pasan a ser un bloque propio ([8139bcc](https://github.com/GuidoAmici/awi-core/commit/8139bcc09cbe7f86e26882d003cb26148353cec7))
* **awi:** ningún identificador viaja desnudo ([5345b2a](https://github.com/GuidoAmici/awi-core/commit/5345b2a5787fdd83e714d28171df938b076addbc))
* **awi:** un comando para el operador se pega y corre ([419fc91](https://github.com/GuidoAmici/awi-core/commit/419fc9197273d92cde5bd28752fe50fd28cc0313))
* **awi:** un commit sin pushear o un PR sin mergear son hilos, no hechos ([f07255f](https://github.com/GuidoAmici/awi-core/commit/f07255f3a89d46cfe14c1cb8a298caab6ab062b9))
* **awi:** worktrees para agentes en paralelo, con artifact ([46529cf](https://github.com/GuidoAmici/awi-core/commit/46529cfc7605871e3496960c6181b6eafeb44b8f))
* **changelog:** rescatar las entradas de 0.2.0 antes de eliminar stg ([2114769](https://github.com/GuidoAmici/awi-core/commit/21147692fdd0de7b35ec10a0284553a4ceb92fb3))
* **contexto:** eliminar employees.json y ordenar el registro de decisiones ([125d839](https://github.com/GuidoAmici/awi-core/commit/125d839aa06f902429c7e7af7a91e3f8a2c01a48))
* **contexto:** reescribir CONTEXT.md y el README sobre el mecanismo real ([2b7b6f2](https://github.com/GuidoAmici/awi-core/commit/2b7b6f2528604f771abdd4f8a8ff83aeba516bd0))
* **harness:** registrar el patrón de artifact-como-brief-mobile en el protocolo ([d3a04a3](https://github.com/GuidoAmici/awi-core/commit/d3a04a346c3a6a91b57cc445834e30cca300a37a))
* **newhaze:** [#193](https://github.com/GuidoAmici/awi-core/issues/193) — decisiones del maintainer y el contrato que hereda [#28](https://github.com/GuidoAmici/awi-core/issues/28) ([80e5d8a](https://github.com/GuidoAmici/awi-core/commit/80e5d8af29ac996345f3d58fa5b4184e30453c10))
* **newhaze:** el fix de db-push se separa del ADR de [#194](https://github.com/GuidoAmici/awi-core/issues/194) y va en su propio PR ([75df988](https://github.com/GuidoAmici/awi-core/commit/75df988ec144162b17d99ea5dfc70dbd1a94760a))
* **newhaze:** el maintainer resolvió el checkbox de [#201](https://github.com/GuidoAmici/awi-core/issues/201) — el nombre de una migración es inmutable ([2e0fa1c](https://github.com/GuidoAmici/awi-core/commit/2e0fa1ceffe9f412223bf6b476f48ea2defc8974))
* **newhaze:** resumen de [#193](https://github.com/GuidoAmici/awi-core/issues/193) — cerrar el INSERT directo de pedidos ([cf48b27](https://github.com/GuidoAmici/awi-core/commit/cf48b2707f716f1f8470e6b2cc5597e9812060e2))
* **newhaze:** resumen del delegate de e2e-playwright (issue [#66](https://github.com/GuidoAmici/awi-core/issues/66)) ([a07fe28](https://github.com/GuidoAmici/awi-core/commit/a07fe28ab910110898d5b2f85fb30717eaadb9d8))
* **newhaze:** resumen del issue [#194](https://github.com/GuidoAmici/awi-core/issues/194) — fantasma reclamables y la colisión de timestamps en db-push ([2080cac](https://github.com/GuidoAmici/awi-core/commit/2080cacf25d0a3b6b30e7c4c10addb69db522292))
* **newhaze:** resumen del overhaul de /catalogo (issue [#195](https://github.com/GuidoAmici/awi-core/issues/195), cuatro slices) ([a82704d](https://github.com/GuidoAmici/awi-core/commit/a82704d01917b139757a9483c1760484cd6ec99b))
* **newhaze:** resúmenes de los delegates de promo badges y donde-comprar ([#21](https://github.com/GuidoAmici/awi-core/issues/21), [#25](https://github.com/GuidoAmici/awi-core/issues/25)) ([8b4f87e](https://github.com/GuidoAmici/awi-core/commit/8b4f87e0861a050e9643ce5de26946b9af3caf95))
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
