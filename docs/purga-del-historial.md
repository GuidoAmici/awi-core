# Purga del historial de awi-core

Registro operativo del PRD 1 ([#80](https://github.com/GuidoAmici/awi-core/issues/80)).
Qué se purga, a quién afecta, cómo se ejecuta, y qué **no** garantiza.

## Por qué

`awi-core` es un repositorio público. En fase 1 (`8334bed`) los archivos de
`.claude/tmp/` se desversionaron y el directorio entró al `.gitignore`. Eso los
sacó del árbol de trabajo, **no del historial**: cualquiera que clone el
repositorio los sigue recibiendo.

Entre ellos hay transcripciones completas de auditorías que agentes delegados
hicieron sobre código de clientes, scripts de migraciones de Supabase, un volcado
SQL con filas, y una credencial de una cuenta de prueba en claro.

## Qué se purga

El conjunto no se escribe a mano: sale del inventario que produce
`history_audit.py`, con las reglas de `.claude/rules/sensitive.json`.

```bash
PYTHONPATH=.claude/skills/shared/scripts \
  python3 .claude/skills/shared/scripts/history_purge.py --repo .
```

Al 2026-07-30 el plan es de **105 rutas**, todas bajo `.claude/tmp/`, señaladas
por regla de ruta: el archivo entero es el problema y no hay nada legítimo que
perder.

### Las tres rutas que quedan afuera

Tres archivos disparan por **contenido** y no por ruta:

| Ruta | Qué tiene |
|---|---|
| `_documentation/_agenda/daily/2026-03-24.md` | una línea con el recuento de severidades de la auditoría de `newhaze-learn` |
| `_documentation/_agenda/planning/2026-Q1.md` | la misma línea, en el plan trimestral |
| `info/organization/daily/2026-03-24.md` | la misma línea, en el árbol de agenda anterior |

Son notas de agenda legítimas del operador que mencionan el recuento agregado de
severidades, no el informe con las vulnerabilidades y su ubicación.
`git-filter-repo` opera por ruta: purgarlas se lleva la nota entera, no la línea.

> El hook bloqueó la primera versión de este párrafo, que citaba el recuento
> textual. Estaba en lo correcto: el documento que explica la purga no necesita
> reproducir el dato que la motivó. La corrección fue reescribir la línea, no
> saltear el hook.

**Decisión: quedan.** El recuento agregado sin el detalle no identifica una
vulnerabilidad explotable, y las tres rutas ya no existen en el árbol actual —
son historia de una estructura de directorios reemplazada. Para incluirlas hay
que pedirlo explícitamente con `--incluir-contenido`, y el precio es que la nota
desaparece completa del historial.

## Impacto — verificado el 2026-07-30

Reescribir el historial cambia todos los SHA, así que cualquier clon o fork
existente queda incapaz de hacer `pull`.

| Qué | Estado |
|---|---|
| Forks | **0** (`forks_count: 0`, `network_count: 0`) |
| Watchers | **0** |
| Colaboradores | **1** — `GuidoAmici`, el dueño |
| `ChristianSRgit`, `nazarenacolqui-ux` | revocados el 2026-07-30; sus clones ya están obsoletos |
| Ramas remotas | `dev`, `main`, y la rama de release-please |

**El impacto conocido es nulo.** Esta es la ventana de menor costo que va a
haber, y es el argumento para ejecutar el PRD 1 antes que los otros cuatro.

Lo que la verificación no puede descartar: el repositorio es público, así que
puede haber clones locales que GitHub no registra. Para esos, la instrucción es
`/awi-update` sobre `main`, que hace reset duro y rescata el trabajo local antes.

## Cómo se ejecuta

La purga **nunca toca el repositorio del operador**. Trabaja sobre un clon
espejo, verifica ahí, y deja el resultado listo para inspeccionar.

```bash
# 1. Espejar, reescribir y verificar. El repo original queda intacto.
PYTHONPATH=.claude/skills/shared/scripts \
  python3 .claude/skills/shared/scripts/history_purge.py --repo . --ejecutar

# 2. Inspeccionar el espejo antes de publicar nada.
git -C ../my-awi-instance-purgado.git log --oneline | head
PYTHONPATH=.claude/skills/shared/scripts \
  python3 .claude/skills/shared/scripts/history_audit.py --repo ../my-awi-instance-purgado.git

# 3. Publicar (irreversible).
git -C ../my-awi-instance-purgado.git remote add origin https://github.com/GuidoAmici/awi-core.git
git -C ../my-awi-instance-purgado.git push --force --mirror origin
```

`--mirror` en las dos puntas: la purga tiene que alcanzar cada rama y cada tag,
porque una rama abandonada sigue publicando lo que tiene.

Después de purgar, la reescritura se verifica volviendo a correr **la misma
auditoría con las mismas reglas** que la motivaron. Si queda algo en una ruta que
la purga declaró haber limpiado, falla ruidosamente. Una purga que no se verifica
con el criterio que la motivó no es una purga, es una esperanza.

### Lo que la primera ejecución real enseñó

Dos defectos que sólo aparecieron al correrlo contra el repositorio de verdad, y
que están como test de regresión:

**`rev-list --objects` deduplica objetos.** Un blob que vivió en dos rutas se
imprime una sola vez, con una de ellas, así que una regla de ruta pierde la otra.
`.claude/tmp/delegates/skill-quality-audit/output.log` —un archivo vacío, y el
blob vacío lo comparten muchos— sobrevivió a la primera purga porque su ruta
nunca entró al inventario. El inventario ahora combina `rev-list --objects` con
`log --raw`, que da el par (blob, ruta) de cada cambio.

**Verificar sólo contra la lista de rutas purgadas es circular.** Una ruta que el
inventario nunca vio quedaba aprobada por no estar en la lista — que es
exactamente cómo el defecto anterior pasó desapercibido. La verificación ahora
replanifica sobre el resultado: cualquier ruta que el plan volvería a señalar es
residuo, incluso si nunca estuvo en la lista.

**`refs/pull/*`.** Un clon `--mirror` de GitHub trae las refs de los pull
requests, que son de sólo lectura del lado del servidor y hacen fallar el
`push --mirror`. Hay que borrarlas del espejo antes de purgar:

```bash
for r in $(git -C espejo.git for-each-ref --format='%(refname)' 'refs/pull/*'); do
  git -C espejo.git update-ref -d "$r"
done
```

**`dev` está protegida contra force-push.** `main`, los tags y la rama de
release-please se actualizaron sin problema; `dev` fue rechazada por su branch
protection (`allow_force_pushes: false`). Hay que desactivarlo en
Settings → Branches → dev, empujar, y volver a activarlo.

### Después

1. **Rotar** la credencial de la cuenta de prueba que estuvo expuesta
   (`.claude/tmp/debug_sb_admin.ps1`). No es opcional — ver el límite, abajo.
2. Cambiar la auditoría de CI de `--rev 'HEAD^{tree}'` a `--all` en
   `.github/workflows/ci.yml`. Mientras el historial no esté purgado, `--all`
   falla siempre por lo conocido, y un gate rojo por algo conocido deja de ser
   una señal.
3. Correr `/awi-update` en cada instancia.
4. Si hay un PR abierto, va a quedar apuntando a commits que ya no existen:
   cerrarlo y reabrirlo desde la rama nueva.

## Lo que la purga NO garantiza

**Reescribir el historial no borra nada en GitHub.** Los objetos quedan sin
referencia, pero siguen siendo accesibles por la API durante un tiempo
indeterminado, y sólo desaparecen del todo pidiéndoselo a soporte o recreando el
repositorio.

La purga **reduce la exposición futura; no la revierte retroactivamente**. Toda
credencial que estuvo expuesta se considera comprometida y se rota,
independientemente de la purga. Esta advertencia va adjunta a cada reporte que
produce `history_audit.py`, para que un reporte vacío no se lea como «el material
dejó de existir».

Fuera del alcance de este trabajo, por ser trámite y no código: pedirle a soporte
de GitHub el borrado de los objetos sin referencia.

## Prevención

Lo que impide que vuelva a pasar es el hook de pre-commit, que usa **exactamente
el mismo motor y el mismo archivo de reglas** que esta auditoría. Con una lista
cada uno, divergirían, y el hook dejaría pasar lo que la auditoría busca.

Se activa por `core.hooksPath`, que es config local y no viaja con un clone: la
activación va en `/awi-update`. Para hacerlo a mano:

```bash
PYTHONPATH=.claude/skills/shared/scripts \
  python3 .claude/skills/shared/scripts/staged_scan.py --instalar
```

El salteo es el mecanismo estándar (`git commit --no-verify`) y queda registrado
en `.git/awi-sensitive-scan-salteos.log`. Para verlos:

```bash
PYTHONPATH=.claude/skills/shared/scripts \
  python3 .claude/skills/shared/scripts/staged_scan.py --salteos
```

## Por qué el repositorio sigue público

Decisión deliberada, registrada en el
[ADR 0014](adr/0014-el-problema-era-la-distribucion-no-la-composicion.md): en el
plan gratuito de GitHub un repositorio privado no ofrece colaboradores de sólo
lectura, así que público sin colaboradores es el control de acceso que se busca.
Eso es lo que eleva esta purga a ser el ítem de más peso de la fase 2.
