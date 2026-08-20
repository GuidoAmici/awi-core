# Artifacts: trazabilidad Artifact ↔ repo

Convención nativa de Claude Code: se apoya en los **Artifacts** de claude.ai y en **Claude Design**. Aplica cada vez que un agente publica un artifact que aporta contenido a un repo — de una org, del harness o del usuario.

**Efímero no quiere decir informal:** el artifact se muestra a compañeros y a clientes, así que se compone con el Design System de la org desde el primer borrador (Regla 0).

**Premisa: el artifact es un prototipo efímero, no el documento.** Su valor es comunicar a compañeros y evolucionar rápido en el corto plazo para nutrir documentos de largo plazo. Un artifact que ya se integró **queda olvidado sin pérdida**, porque lo que tenía que persistir ya vive en el repo. Si perder el artifact duele, es que la Regla 1 o la Regla 3 no se cumplieron.

## Las ocho reglas de un vistazo

| # | Regla | En una línea |
|---|---|---|
| 0 | Forma del Design System | Todo artifact se compone con el Design System de la org destinataria. Se resuelve antes de escribir la primera línea. |
| 1 | Fuente en el repo | El HTML/MD fuente se versiona en git, junto al material que apunta. Nunca en el scratchpad. |
| 2 | Trazabilidad bidireccional | El repo apunta al artifact; el artifact declara al pie qué entrega y a qué archivo. |
| 3 | Reparto de contenido | Lo esencial y actualizado en el repo; el detalle y el razonamiento en el artifact. |
| 4 | Deprecación, no borrado | Cuando el repo deja de apuntarlo: fecha de deprecación + link al reemplazo. |
| 5 | Destino correcto | Design System, docs de identidad o BDR — no siempre es el Design System. |
| 6 | Escaneo primero | Métricas, tablas de estado y veredictos arriba; el detalle en `<details>`. |
| 7 | Issue padre | Si hay entregas pendientes de integrar, hay un issue con label `artifact`. |

---

## Regla 0 — La forma la pone el Design System de la org

**Ningún artifact se diseña desde cero.** Antes de escribir la primera línea de HTML se resuelve a qué org entrega el artifact (Regla 5) y se abre el Design System de esa org. La paleta, la tipografía, los componentes, la voz y el logo salen de ahí — no del gusto del agente ni de los defaults de la herramienta.

Es la Regla 0 y no la 8 porque es una **precondición**: llegar al final del artifact y "aplicarle la marca" no funciona. La forma condiciona qué se puede mostrar.

### Dónde vive el Design System

Convención vigente — el DS de una org es un directorio dentro de sus docs de identidad:

```
_data/organizations/<org>/documentation/identidad/<Nombre> Design System (vN)/
├── SKILL.md          ← se lee primero: reglas de marca que nunca se rompen
├── readme.md         ← la guía completa: contexto, voz, fundamentos visuales
├── styles.css        ← entry point que importa todos los tokens
├── tokens/           ← colors, fonts, typography, spacing, effects
├── components/       ← primitivas reutilizables, cada una con su .prompt.md
├── assets/           ← vectores reales del logo (nunca se redibuja el mark)
└── guidelines/       ← specimen cards de las fundaciones
```

Ejemplo real: [`New Haze Design System (v2)`](../../_data/organizations/newhaze/documentation/identidad/). Su `SKILL.md` es además una skill invocable — si está cargada, invocarla equivale a leer el DS.

Si la org no tiene DS bajo esa ruta, se busca en `documentation/` antes de concluir que no existe (en `afin` vive como un solo `.md`: `documentation/modernizacion/design-system.md`).

### El DS se copia al artifact, no se referencia

El CSP de los Artifacts bloquea **todo host externo**: nada de CDN, hojas de estilo remotas, webfonts o imágenes por URL. Un `@import` al `styles.css` del DS tampoco sirve, porque el artifact publicado es un archivo suelto sin el árbol del repo alrededor.

Consecuencia práctica: el DS viaja **dentro** del artifact. Tokens inline, webfonts como `data:` URI, logos como SVG inline copiado de `assets/`.

De ahí el patrón que ya usa `newhaze` y que conviene replicar: un `_sistema-visual.css` compartido —fuentes embebidas + tokens + componentes— que un `build.py` inyecta en cada `<slug>.body.html` para producir el `<slug>.html` publicable. El fuente que se edita es el `.body.html`; el `.html` es artefacto de build.

### Los nombres de los tokens son los del Design System

Al copiar el DS al artifact **se conservan los nombres de los tokens**. Renombrar `--nh-brand` a `--brand` porque queda más corto crea un alias silencioso: hoy los dos valen `#7A58F0`, mañana el DS mueve el violeta y el artifact sigue con el viejo, sin que nada avise y sin que ningún grep los relacione.

> **Estado actual, para no repetirlo:** `documentation/identidad/_sistema-visual.css` de `newhaze` hace exactamente eso — `--brand`, `--ink`, `--surface`, `--data` son copias renombradas de `--nh-brand`, `--nh-text-primary`, `--nh-bg-surface`, `--nh-accent`. Los valores coinciden hoy por casualidad, no por mecanismo. Es deuda conocida (ver *Pendiente 9*), no un patrón a imitar.

### Reglas rápidas derivadas

- **Nada de paleta o tipografía ad hoc.** Si el artifact necesita un color, un componente o un espaciado que el DS no tiene, no se inventa en el artifact: se decide, se usa, y esa decisión entra al DS por la Regla 5 como cualquier otra entrega.
- **Las reglas de marca del `SKILL.md` mandan sobre cualquier default.** En New Haze: voseo, sin emoji, mediciones en JetBrains Mono, dark-first, el mark no se redibuja.
- **El skill `artifact-design` es el piso, no el techo.** Aporta fundamentos de composición; cuando choca con el DS de la org, gana el DS.
- **Si la org no tiene DS**, se compone con `artifact-design` y el pie del artifact (Regla 2) lo declara: `Design System — ninguno vigente para esta org`. No se simula uno.
- **Única excepción:** el artifact que *propone* identidad nueva —un rebranding, una exploración de marca— se aparta del DS a propósito, porque apartarse **es** el contenido. Aun así declara de qué DS vigente se aparta.

---

## Regla 1 — Los fuentes viven en el repo

El archivo HTML o MD fuente de todo artifact **se versiona en git, junto al material que apunta**. Nunca en el scratchpad de sesión.

```
documentation/identidad/artifacts/arquitectura-de-marca.html   ✅ versionado, junto a identidad/
/tmp/claude-…/scratchpad/arquitectura-de-marca.html            ❌ desaparece con la sesión
```

**Por qué — el motivo técnico, que es la razón de ser de la regla:** la herramienta `Artifact` conserva la URL de un artifact **sólo si se lo redeploya desde el mismo `file_path`**. Un archivo distinto acuña una URL nueva aunque el contenido sea el mismo documento.

Consecuencia: si el fuente vivió en un scratchpad de sesión, meses después el artifact **ya no se puede actualizar**. Sólo se puede recrear en otra URL — y todos los links del repo quedan apuntando a una versión vieja **sin que nada avise**. El link sigue resolviendo, sigue viéndose bien, y miente.

Reglas rápidas derivadas:

- Redeploy = mismo `file_path`. Si el archivo se mueve o se renombra, la URL se pierde.
- Un artifact publicado en otra conversación se actualiza pasando su `url` a la herramienta, además del `file_path`.
- El fuente se commitea **antes o junto con** la publicación, no después.

---

## Regla 2 — Trazabilidad bidireccional

Cada dirección tiene su propio soporte. Las dos son obligatorias.

| Dirección | Dónde vive | Qué lleva |
|---|---|---|
| Repo → artifact | El archivo del repo | Fecha de **última actualización** + link al/los artifact(s) que dieron lugar a esa actualización de contexto |
| Artifact → repo | Bloque al **pie** del artifact | Qué entrega, a qué archivo, y en qué estado está esa entrega |

Estados de una entrega: `pendiente` | `integrado`.

---

## Regla 3 — Reparto de contenido

| Va al repo | Va al artifact |
|---|---|
| La información esencial, lo más actualizada posible | El detalle no esencial |
| El resultado: la decisión, el token, el guideline, la definición | El desarrollo del razonamiento: pruebas, variantes evaluadas, decisiones descartadas y por qué |

Si el razonamiento completo se copia al repo, el repo deja de ser escaneable. Si el resultado sólo vive en el artifact, el repo deja de ser confiable. La frontera es esa.

---

## Regla 4 — Ciclo de deprecación

Cuando un artifact **deja de estar apuntado desde el repo**, se lo edita agregándole:

1. **Fecha de deprecación**
2. **Link al artifact de reemplazo**

**No se borra.** Los links viejos —en chats, en issues, en mails a compañeros— tienen que seguir resolviendo y tienen que contar que hay algo más nuevo.

---

## Regla 5 — Destinos de largo plazo

Un artifact **no siempre apunta al Design System**. Elegir el destino correcto es parte de la entrega:

| Tipo de contenido | Destino |
|---|---|
| Diseño: tokens, componentes, guidelines, logo, voz | El **Design System** del proyecto |
| Narrativa de marca, misión/visión, arquitectura de marca | Los **docs de identidad** del proyecto (`documentation/identidad/*.md`) |
| Decisiones de negocio | Un **BDR** (`documentation/bdr/`) |

**El Design System tiene dos roles y no hay que confundirlos.** Por la Regla 0 es la **fuente de la forma** de *todos* los artifacts, sin excepción. Por esta regla es el **destino del contenido** sólo de algunos. Un artifact sobre pricing se compone con el DS y no le entrega nada; uno sobre tokens se compone con el DS y además le entrega.

---

## Regla 6 — Forma de los artifacts

**Capa de escaneo primero, detalle después.**

- Arriba: métricas grandes, tablas de estado, veredictos.
- Abajo: el detalle, preferiblemente dentro de desplegables (`<details>`).

El criterio del maintainer, textual:

> "El humano prefiere comprender rápidamente por un escaneo visual, y luego volver al detalle cuando lo necesita."

---

## Regla 7 — Issue padre

Cada vez que haya **ítems pendientes de integración**, se abre un **issue padre con label `artifact`** en el repo que corresponda según [`docs/agents/issue-tracker.md`](issue-tracker.md).

Recordatorio de ruteo (la tabla completa está en ese archivo):

| El contenido entrega a… | Issue en |
|---|---|
| Identidad, marca, Design System, BDR de una org | El workspace repo de esa org |
| El harness de AWI | `GuidoAmici/awi-core` |
| Material estrictamente personal | `GuidoAmici/my-awi-user` |

---

## Bloques listos para copiar

### Encabezado del archivo de repo (Regla 2, repo → artifact)

Sobre el frontmatter YAML que ya usan los docs del vault:

```yaml
---
tipo: identidad
capa: marca
descripcion: Misión, visión, valores y arquitectura de marca.
last-updated: 2026-08-06
artifacts:
  - url: https://claude.ai/public/artifacts/<id>
    entrega: Arquitectura de marca — 3 niveles y criterio de nombres
    estado: integrado
    fecha: 2026-08-06
---
```

`last-updated` es la fecha de la última actualización del archivo. `artifacts:` lista los artifacts que dieron lugar a esa actualización de contexto — no todos los que existieron alguna vez.

### Pie del artifact (Regla 2, artifact → repo)

En HTML:

```html
<footer class="entrega">
  <h2>Entrega</h2>
  <table>
    <tr><th>Qué entrega</th><td>Arquitectura de marca — 3 niveles y criterio de nombres</td></tr>
    <tr><th>Archivo destino</th><td><code>documentation/identidad/marca.md</code> · <code>GuidoAmici/newhaze-workspace</code></td></tr>
    <tr><th>Estado</th><td><strong>pendiente</strong></td></tr>
    <tr><th>Issue padre</th><td>GuidoAmici/newhaze-workspace#128</td></tr>
    <tr><th>Fuente versionado</th><td><code>documentation/identidad/artifacts/arquitectura-de-marca.html</code></td></tr>
    <tr><th>Design System</th><td>New Haze Design System (v2)</td></tr>
  </table>
</footer>
```

La fila **Design System** declara con qué DS se compuso (Regla 0). Valores posibles: el nombre y versión del DS, `ninguno vigente para esta org`, o `se aparta de <DS> — el artifact propone identidad nueva`.

En Markdown:

```markdown
---

## Entrega

| | |
|---|---|
| **Qué entrega** | Arquitectura de marca — 3 niveles y criterio de nombres |
| **Archivo destino** | `documentation/identidad/marca.md` · `GuidoAmici/newhaze-workspace` |
| **Estado** | **pendiente** |
| **Issue padre** | GuidoAmici/newhaze-workspace#128 |
| **Fuente versionado** | `documentation/identidad/artifacts/arquitectura-de-marca.html` |
| **Design System** | New Haze Design System (v2) |
```

### Aviso de deprecación (Regla 4)

Se agrega **arriba de todo** en el artifact deprecado, y se redeploya desde el mismo `file_path`:

```html
<aside class="deprecado">
  <strong>Deprecado el 2026-09-12.</strong>
  Reemplazado por <a href="https://claude.ai/public/artifacts/&lt;id-nuevo&gt;">Arquitectura de marca (v2)</a>.
</aside>
```

---

## Pendiente de definir

Huecos detectados al documentar el protocolo. No están resueltos por el acuerdo original — los bloques de arriba proponen una forma, pero la decisión sigue abierta.

1. **Nombre y forma del campo de frontmatter.** El acuerdo fija *qué* debe llevar el archivo del repo (fecha + links), no *cómo*. `artifacts:` con subcampos `url`/`entrega`/`estado`/`fecha` es una propuesta de este documento, no una convención acordada.
2. **Ubicación canónica del fuente.** La Regla 1 dice "junto al material que apunta". En `newhaze` ya existe `documentation/identidad/artifacts/`, y este documento lo toma como patrón — pero no está definido si esa carpeta `artifacts/` es la convención general ni qué pasa cuando el material apuntado es un directorio (p. ej. el Design System) en lugar de un `.md`.
3. **Quién marca `integrado`, y cuándo.** Los dos estados están definidos; el disparador no. ¿Se marca al commitear el destino, al cerrar el issue padre, o lo confirma el maintainer?
4. **Cierre del issue padre.** No está definido si el issue se cierra cuando todas sus entregas pasan a `integrado`, ni qué pasa con un issue padre que acumula entregas de varios artifacts a lo largo del tiempo.
5. **Artifacts descartados.** La Regla 4 cubre el reemplazo (hay un sucesor). No cubre el caso de un artifact que nunca se integra y no tiene reemplazo: ¿se deprecia sin link, se marca `descartado`, o queda como está?
6. **Tensión Regla 1 ↔ Regla 4.** Un artifact de reemplazo tiene URL nueva, y por la Regla 1 eso implica **un archivo fuente nuevo** en el repo. Queda sin definir cómo se nombran los dos fuentes que conviven (¿sufijo `-v2`? ¿el viejo se mueve a un `deprecados/`?) sin romper el `file_path` del deprecado, que debe seguir redeployable para poder editarle el aviso.
7. **Entregas a más de un destino.** No está definido si un mismo artifact puede declarar varios archivos destino, ni cómo se representa un estado parcial (integrado en uno, pendiente en otro).
8. **Privacidad y momento de compartir.** Un artifact nace privado. El protocolo no dice en qué momento se comparte con los compañeros ni si ese hecho se registra en algún lado.
9. **Cómo se deriva el bundle del Design System.** La Regla 0 fija *qué* debe cumplir el CSS embebido (mismos valores, mismos nombres que el DS), no *cómo* se produce. Hoy `_sistema-visual.css` se mantiene a mano y ya divergió en nombres. Falta decidir si se genera con un script desde `tokens/*.css`, si el `build.py` de cada carpeta `artifacts/` lo hace en el momento, o si el DS publica un bundle autocontenido listo para embeber. Mientras tanto, cada artifact nuevo copia los nombres `--nh-*` tal cual.
10. **Versionado del DS en artifacts vivos.** Cuando el DS pasa a v3, los artifacts publicados con v2 quedan con la forma vieja. No está definido si se redeployan (conservan URL, así que es posible), si se deprecian, o si se los deja como registro de época.
11. **Artifact como brief de tareas — patrón validado, sin nombre todavía.** El 2026-08-11, `newhaze` publicó un artifact con el plan del día para una persona del equipo (no un compañero técnico): panorama primero, detalle de cada tarea después, textos listos para copiar. Funcionó — claro, cómodo de leer, y sobre todo **accesible desde el celular**, que es el hueco real de AWI: el harness pide instalación en una PC y no tiene story mobile. El artifact puntual (`49758f0d`) se depreció el 20/08 porque era un brief fechado del 11/08, no porque el patrón fallara. Queda sin resolver: ¿es un caso más de "artifact que aporta contenido a un repo" (y entonces las ocho reglas de arriba ya lo cubren), o es un uso distinto —brief operativo de un día, para una persona, con vida útil de 24 h— que merece su propia convención (dónde vive el fuente, si versiona en `agenda/daily/` en vez de `documentation/`, si tiene sentido pedirle Regla 1–2 a algo que nace y muere en un día)? Vale mirarlo de nuevo si vuelve a aparecer la necesidad.
