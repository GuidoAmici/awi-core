# El problema era la distribución, no la composición

> **Cierra [ADR 0013](0013-revision-integral-de-awi-core.md).** La revisión integral se hizo el 2026-07-29.
> Su resultado no es "conservar" ni "rehacer": es que la pregunta estaba mal planteada, porque
> awi-core no es una base uniforme sino tres capas con salud muy distinta.

Los trece ADRs anteriores discuten **composición**: cómo acomodar unidades de información en una máquina. Submódulos contra manifiestos, quién es dueño del árbol, dónde pinear. Esa discusión está resuelta, y el [ADR 0011](0011-la-composicion-es-una-capa-con-dueno.md) nombró bien el problema de dominio que la sostiene.

Lo que rompe el sistema en producción es otra cosa: **cómo un cambio llega a otra máquina.** No hay ningún ADR sobre eso, no hay código que lo haga, y es la causa directa de los dos dolores concretos que el operador reportó — tener que arreglar la instancia de cada compañero a mano, y dejar de usar `/awi-sync`.

La revisión encontró el mecanismo de los dos:

**El canal hacia las instancias no existe.** El commit `ba2323c` eliminó `pull_from_awi_core()` razonando *"la instancia pasó a **ser** awi-core"*. Es cierto en la máquina del operador —`origin` apunta a awi-core— y falso en las de sus compañeros, que corren instancias que no son awi-core. El mismo commit admite que el canal ya venía fallando en cada corrida antes de ser borrado por muerto. Y la rama por defecto del repo es `prod`, que es lo que recibe cualquiera que clona, y que estaba 11 commits atrás de `dev` porque sólo avanza cuando alguien mergea a mano un PR de release. No había ni canal automático ni una rama que se moviera sola.

**El sync de contexto deja los repos a medias.** `/awi-sync` hace `git add -A`, commitea con el mensaje fijo `"chore(sync): stage local changes"`, y hace `pull --rebase`. Con un operador funciona. Con varios editando el mismo markdown, el rebase choca; y cuando choca, el script marca `failed`, retorna y sigue con el próximo repo **sin hacer `rebase --abort`**. Deja el repo a mitad de un rebase, en un estado que se sale con comandos de git, a personas que por diseño no saben git.

## Lo que la revisión confirmó del diagnóstico del 0013

El 0013 describió un patrón —migraciones a medias que dejan residuo activo— con cuatro síntomas. Hay siete instancias verificadas:

| Residuo | Evidencia |
|---|---|
| `.gitignore` cita `generate_gitmodules.py` (borrado) y el ADR 0001 (supersedido) | ya registrado en el 0013 |
| `CONTEXT.md` define el dominio entero en términos de submódulos | *Initialize* = `git submodule update --init` |
| `README.md` documenta auto-commit y el prefijo `cos:`, ambos eliminados | |
| `employees.json`, 36 entradas, leído por 2 skills, pese al [ADR 0008](0008-agent-discovery-desde-agency-agents.md) | |
| `pull_from_awi_core()` borrado razonando desde el caso de un solo operador | `ba2323c` |
| `promote-dev-to-stg.yml` duplica el merge de `dev.yml` y falla en el 100% de los pushes | 4 de 4 corridas |
| `ci-dev.yml` duplica el job de test de `dev.yml`, con la invocación de pytest rota | nunca se nota |
| `CLAUDE.md` declara "No auto-commit hook" mientras `/awi-sync` auto-commitea | 73 corridas registradas |

Más la duplicación estructural: cuatro copias de la misma skill de scaffolding, tres de ellas byte-idénticas, y once skills triplicadas entre `.agents/`, `.claude/` y el plugin `mattpocock-skills`.

Los workflows merecen una aclaración, porque la primera lectura de la revisión fue equivocada. **El gate existe y funciona**: `dev.yml` corre `pytest -q tests` y los nueve tests pasan en cada push. Lo que hay son dos duplicados suyos que no aportan nada. `ci-dev.yml` repite el job de test con una invocación que colecta los 33 archivos de script en lugar de `tests/` —termina en error interno y `no tests ran`—, y su inutilidad pasa inadvertida porque `dev.yml` ya cubre el mismo trigger, `push` y `pull_request` sobre `dev`. `promote-dev-to-stg.yml` repite el merge con un token que no puede saltar las reglas de rama, y por eso falla siempre mientras el merge real lo hace `dev.yml`.

## Lo que se conserva

La revisión validó una capa y la deja intacta: **los manifiestos y la materialización.** El corte por propiedad entre `user-submodules.json` (privado, portable) y `codebases.json` (versionado en cada org) es la mejor decisión del sistema, y `plan()` resuelve los nueve repos con los nueve materializados. Rehacer desde cero obligaría a redecidir eso, que es lo único que la revisión encontró sano y en uso diario.

Las otras dos capas se rehacen. La de skills, porque ahí vive el residuo. La de harness y delegación, porque nunca tuvo requisitos escritos: `--dangerously-skip-permissions` sobre doce servidores MCP con credenciales no es deuda técnica, es una decisión que nadie tomó.

## Decisiones

**El problema de dominio se amplía.** Al enunciado del 0011 —componer unidades con dueños y ciclos de vida distintos en una vista coherente— se le agrega: **y propagar los cambios de esa composición a las máquinas de los demás operadores.** La composición es una capa; la distribución es otra, y es la que falta.

**La base se conserva partida por capa**, no entera ni descartada. Manifiestos y materialización quedan. Skills y harness se rehacen.

**El trabajo se parte en dos fases.** Fase 1 deja funcionando lo que hay, porque otros operadores dependen de esto hoy. Fase 2 rediseña desde la base.

**La pregunta del sustrato queda abierta a propósito.** Si el destino —frontend sobre ERP con datos de clientes— corre sobre git o sobre una base de datos no está decidido. De ahí sale el criterio que gobierna la fase 1: **reversibilidad.** No se construye nada que dé la pregunta por respondida. Eso mantiene diferidos la capa 3 del [0011](0011-la-composicion-es-una-capa-con-dueno.md) y el campo `rev` del [0012](0012-contextos-flotan-dependencias-pinean.md), ahora por una razón mejor que "esperemos a la revisión": ambos son apuestas a que git es el sustrato definitivo, y el invariante del 0011 —*toda ruta pertenece a exactamente un repo*— es lo primero que se cae si la mitad de los datos pasa a vivir en una base.

**Los compañeros son consumidores del harness, no coautores.** `/awi-update` hace reset duro sobre los archivos del harness y deja `_data/` intacto. Sin merge no hay conflicto, y no hay conflicto que mostrarle a alguien que no sabe git. Es la frontera de propiedad del 0011 aplicada a personas en lugar de a repos.

**Una sola rama de distribución.** Se colapsan `dev`, `stg` y `prod`. El gate no hay que construirlo: son los nueve tests que `dev.yml` ya corre, reapuntados a la rama única. Se eliminan los dos workflows duplicados.

**`/awi-sync` se depreca.** Nació para reapuntar submódulos, que ya no existen. Lo reemplaza la IA coordinando el ciclo: pull de los repos de org al inicio de sesión, commit y push sugeridos al cerrar o en cortes lógicos, mensajes redactados por la IA, y consulta al usuario ante conflicto de datos.

**El juicio va en instrucciones, la mecánica en código.** Cuándo pullear, cuándo sugerir commit, cómo nombrarlo y si preguntar es juicio, y vive en `INSTRUCTIONS.md`. Pullear, abortar limpio ante conflicto, pushear y reportar es mecánica determinística, y vive en código con tests. La razón es empírica: `log_command` se invoca por instrucción en 22 archivos `SKILL.md` y el registro subcuenta —29 skills sin una sola aparición en 272 invocaciones—, así que sabemos que las instrucciones se cumplen a veces. Para un log, "a veces" alcanza. Para traer el contexto de otro operador, "a veces" significa trabajar sobre datos viejos sin enterarse.

**Semver y changelog se conservan, fuera del camino de distribución.** Lo que congelaba no era el versionado sino el pipeline de promoción de tres ramas. release-please se reapunta a la rama única y produce `CHANGELOG.md`, que nunca se generó. `/awi-update` consume la punta de la rama, no el último tag: los cambios llegan sin gate, y cortar versión vuelve a ser un acto deliberado que no bloquea a nadie. El changelog pasa a ser la parte visible del canal —un compañero que actualiza lee "esto cambió" en castellano en lugar de un `git log`—, y por eso los mensajes que redacte la IA tienen que ser Conventional Commits: son su materia prima.

**AWI vuelve a ser Claude-native.** Se eliminan `.agents/`, `GEMINI.md`, `.gemini/` y `AGENTS.md`. Para las once skills triplicadas gana el plugin, y se borra también la copia de `.claude/`.

**El riesgo de permisos de los delegates se acepta hasta la fase 2.** Un delegate corre desatendido con acceso a doppler, supabase, mercadopago y gmail, y su prompt sale de un comentario de issue, que es contenido externo y editable. El operador asume el riesgo con la información a la vista, y la aceptación es válida **mientras sea el único que corre delegates**. Si un compañero usa `/delegate-issue`, el cálculo cambia. Sí entran en fase 1 un timeout y un tope de gasto, que no son seguridad sino costo: hoy un delegate colgado corre indefinido.

## Consecuencias

- El 0013 queda cerrado. Los 0011 y 0012 siguen decididos y no implementados, ahora por el criterio de reversibilidad y no por espera.
- El residuo de `.gitignore` se limpia en fase 1, junto con la salida de `.claude/tmp` del árbol.
- `awi-core` pasa a privado. Había credenciales en claro en varios `.ps1` bajo `.claude/tmp` en un repo público, y el repo se comparte con compañeros por clonado. La purga del historial va a fase 2; la rotación es inmediata.
- La numeración y el idioma de los ADRs quedan diferidos a fase 2, contra lo que anticipaba el 0013. Renumerar rompe los enlaces cruzados entre ADRs, y ese trabajo no puede colarse en la fase que existe para dejar el sistema funcionando. Este ADR es el 0014 bajo el esquema actual.
- Que el sustrato siga abierto es una propiedad del estado del producto, no una postura. La fase 2 empieza por ahí, y el criterio de reversibilidad se levanta cuando la pregunta se responda.
