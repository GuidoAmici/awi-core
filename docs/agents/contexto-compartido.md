# Contexto compartido

Los repos de contexto —las orgs, sus codebases y el repo del propio operador— los editan **varias personas**. Traer y publicar los cambios es responsabilidad tuya, no del operador: la idea es que nadie tenga que saber git para trabajar acompañado.

La mecánica está en `context_sync.py`; el juicio de cuándo usarla es esto. No reimplementes la mecánica con comandos de git sueltos — el script existe porque un `pull --rebase` mal manejado deja repos a medias, y eso ya pasó.

# Los momentos, y por qué están anclados en skills

Esta sección existía y no se cumplía. La comprobación es directa: `context_sync.py status` encontró trabajo sin publicar en cinco repos a la vez, y en el workspace de una org el aporte más reciente de otra operadora llevaba tres semanas sin que nadie lo trajera. El mismo modo de falla que ya se había documentado para `log_command`, que subcuenta porque depende de que 22 archivos se acuerden de invocarlo.

Por eso cada momento está **anclado como paso de la skill que lo abre**, y acá queda el porqué en un solo lugar. Ver [ADR 0020](../adr/0020-el-ciclo-de-contexto-se-ancla-en-las-skills.md).

| Momento | Qué | Anclado en |
|---|---|---|
| Abrir o refrescar el día | traer | `/today` |
| Antes de leer el tracker | traer | `/triage`, `/delegate-issue` |
| Empezar un descanso | publicar | `/break <motivo>` |
| Volver de un descanso | traer | `/break back` |
| Cerrar la sesión | publicar | `/wrap-session` |

Si estás en uno de esos momentos y la skill no corrió el paso, corrélo igual. La tabla manda sobre el archivo.

# Traer — sin preguntar

```bash
python3 .claude/skills/shared/scripts/context_sync.py pull
```

Antes de leer o escribir contexto, y sin pedir permiso: trabajar sobre datos viejos es peor que la interrupción. Es rápido y no destruye nada.

# Publicar — sin preguntar, pero contándolo

```bash
python3 .claude/skills/shared/scripts/context_sync.py status
python3 .claude/skills/shared/scripts/context_sync.py push --repo <nombre> --message "<mensaje>"
```

Mirá `status`, y publicá lo que haya **sin pedir confirmación**. Después contá en una línea por repo qué se publicó. La confirmación previa se sacó porque el costo de pedirla resultó ser que no se publicara nada: quien trabaja acompañado necesita que su contexto llegue al otro lado, no un permiso más que dar.

**Redactá vos el mensaje de cada repo, uno por repo.** En [Conventional Commits](../../_system/_agentic-workflow-integrator/references/commit-format.md), describiendo lo que cambió de verdad. Nunca un mensaje genérico repetido: el historial compartido de estos repos es una pared de `chore(sync): stage local changes` porque el sync viejo usaba una constante, y eso lo vuelve inservible para saber qué pasó.

Publicar automáticamente sólo es aceptable con la red debajo: `push` escanea el material sensible antes de tocar el índice, con las mismas reglas que el hook de pre-commit. El hook no alcanza a estos repos —`core.hooksPath` apunta a un directorio del harness y ellos son repos aparte, en `_data/`— así que el escaneo vive dentro del script.

# Cuando un repo reporta `conflicto`

Significa que los cambios del operador y los de otra persona se pisan. **El repo quedó como estaba** — el script nunca lo deja a mitad de una operación.

No lo resuelvas por tu cuenta: decidir qué versión del trabajo de otra persona sobrevive no es tuyo. Mostrale al operador qué repo es y qué se toca, y preguntale cómo seguir. El resto de los repos sí se sincronizó, así que la sesión puede continuar.

# Cuando un repo reporta `sensible`

Hay una credencial o material de cliente entre los cambios. **No se commiteó ni publicó nada, y el índice quedó intacto.** Mostrale al operador las rutas señaladas y el remedio de cada regla; sacar el archivo, rotar la credencial o ajustar la regla son decisiones suyas. Los demás repos sí se publicaron.

# Cuando un repo reporta `otra-rama`

El operador está trabajando en una rama distinta de la que el manifiesto declara — una rama de feature en un codebase es lo normal, no la excepción. El ciclo no publica ahí: el commit iría a la rama activa y el push subiría la del manifiesto, así que «publicado» significaría que el trabajo quedó en local mientras se subía otra cosa.

Decíselo y preguntá. Mergear, abrir un PR o cambiar de rama son decisiones del operador, y ninguna es del ciclo de contexto.

# Qué no entra en este ciclo

- **Los codebases.** Su contenido no es contexto que se pasa entre operadores: es código. Avanza en su propia sesión, con el desarrollador mirando, y por eso ni se trae ni se publica automáticamente. `status` los lista igual —enterarse de que hay trabajo sin publicar es útil— pero no los toca, y `push --repo <codebase>` falla con una explicación. Si estás **en** esa sesión de desarrollo y el operador lo pide, `--con-codebases` los habilita.
- **El harness.** Se actualiza con `/awi-update`, que es otra cosa: ahí el operador es consumidor y no coautor. En la instancia del mantenedor, donde el harness sí se edita, sus commits se publican como cualquier otro trabajo terminado — con git, no con este ciclo.
- **Los repos `upstream`.** Son dependencias, no contexto ([ADR 0012](../adr/0012-contextos-flotan-dependencias-pinean.md)), y su política de versionado es distinta.
