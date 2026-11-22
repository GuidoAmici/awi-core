# La agenda envejece; la documentación se mantiene

> **Estado: aceptado (2026-11-17).** Lo pidió el operador después de revisar
> `newhaze` y `afin` contra el scaffold.

## Contexto

El scaffold de un Org Workspace crea `agenda/` y `documentation/` pero nunca dijo
con qué criterio algo va a una o a otra. De `documentation/` sólo decía «estilo de
escritura, perfil, wiki». Y `outputs/` estaba definido dos veces, en contradicción:
`scaffold.py` lo llamaba «entregables e informes»; `file-formats.md` le daba la
forma de un registro de decisión (*What changed / Why / Trade-offs* y `affects:`).

Sin criterio, cada sesión decidió por su cuenta, y la org con más uso juntó todas
esas decisiones. Medido en `newhaze` el 2026-11-14:

- `agenda/outputs/` tenía 68 `.md` y 9 carpetas con scripts y renders, mezclando
  cinco cosas: decisiones, documentos vigentes (política de privacidad, términos,
  garantía, FAQ), piezas de producción (guiones, prompts), informes de issues y
  estados de release. 57 de los 68 no llevaban `affects:`.
- Las decisiones vivían en cuatro lugares: `documentation/bdr/`,
  `documentation/arquitectura-digital/adr/`, `documentation/prd/` y `agenda/outputs/`.
- Aparecieron carpetas fuera del canon: `agenda/companies/` y
  `agenda/sales-proposals/`. Hubo handoffs en `documentation/` y listas de precios
  en la raíz de `documentation/`.
- `documentation/identidad/` tenía `package.json`, `node_modules` y generadores:
  código guardado como documentación.

`afin`, con poco uso, ya mostraba el mismo patrón: una propuesta de venta en
`outputs/` (newhaze las ponía en `sales-proposals/`) y una carpeta de proyecto
(`modernizacion/`) en `documentation/`.

## La decisión

Una sola pregunta decide la capa: **¿envejece solo?**

- **`documentation/` es lo que es verdad hoy.** Se sobrescribe cuando cambia y se
  lee para actuar. Se ordena por **tema permanente** —producto, área, marca—,
  nunca por proyecto: el proyecto termina y lo que se supo sigue valiendo.
- **`agenda/` es lo que pasó o lo que falta que pase.** Va fechado, se acumula y
  no se reescribe.

Que un tema aparezca en las dos capas está bien si cada lado guarda lo suyo:
`agenda/projects/kit-riego-automatico.md` es la iniciativa —estado, próxima
acción, bitácora— y `documentation/productos/kit-riego/` es lo que se sabe del
producto.

### Dónde va cada cosa

| Qué es | Dónde va |
|---|---|
| Una decisión vigente de arquitectura | `documentation/adr/NNNN-<slug>.md` |
| Una decisión vigente de negocio | `documentation/bdr/NNNN-<slug>.md` ([plantilla](../../_system/chief-of-staff/references/bdr-template.md)) |
| Una decisión sobre el código de un codebase | `docs/adr/` de ese codebase |
| Un análisis, investigación o informe fechado | `agenda/outputs/YYYY-MM-DD-<slug>.md` |
| Una pieza entregada o publicada a un tercero (propuesta, lista de precios, guion) | `agenda/deliverables/YYYY-MM-DD-<slug>` |
| Una empresa con la que hay relación (cliente, proveedor) | `agenda/companies/<Nombre>.md` |
| Un traspaso entre sesiones | `agenda/handoffs/`, como hasta ahora |
| La bitácora de un proyecto | El archivo del proyecto en `agenda/projects/` |
| Un procedimiento, una política o un precio vigente | `documentation/<tema>/` |
| Algo con `package.json`, scripts de build o dependencias | Un codebase propio |

**Las decisiones salen de `outputs/`.** Una decisión vigente es verdad hoy, así
que es documentación. Un output pasa a ser el análisis fechado que la fundamentó,
y la enlaza. Esto reemplaza la regla de que «toda decisión va como output».

**El entregable tiene carpeta propia y no un campo.** Se descartó `kind:` en el
frontmatter de los outputs por dos razones: `kind: decision` chocaba con los BDR,
que ya son decisiones, y un campo no se ve en el filetree, que es justo donde
estaba el problema.

### Lo vigente lleva sus cambios

Cada documento vigente cierra con una sección `## Cambios`, una línea por cambio
de fondo (un precio, una regla, una política), nunca por erratas:

```markdown
## Cambios

- 2026-11-12 · Mínimo de pedido G2: 6 → 10 unidades · [BDR-0012](../bdr/0012-…)
```

El historial de git no alcanza solo. Tiene el cambio literal, y en las orgs los
mensajes son buenos, pero: la IA no lo consulta si nadie se lo pide, pesa igual
un precio que una errata, se corta con cada `git mv` si no se usa `--follow`, y
dice qué cambió pero no qué decisión lo causó. La sección es el índice; git
sigue teniendo el detalle.

Va **adentro** del documento y no en un `changelog.md` aparte: un archivo
separado envejece sin que nadie lo note, que es el problema que viene a
resolver.

### El manual de marca no sale del repo de la org

La regla del código tiene una excepción a propósito. Un codebase es opcional:
cada operador elige en su `user-submodules.json` si lo baja, y en GitHub el
acceso a otro repo se da aparte. El manual de marca y los tokens de color tienen
que estar en disco para **cualquiera que trabaje la org**, así que se quedan en
`documentation/identidad/`. Lo que sale a un codebase son los generadores que
**usan** esos tokens: leen los del repo de la org, no se guardan una copia.

## Lo que se descartó

- **Confiar sólo en el historial de git** para saber qué cambió. Ver arriba.
- **`documentation/decisiones/{adr,bdr}/`.** Es otro nivel de carpetas sin
  ganancia: `bdr-template.md` ya fijaba `documentation/bdr/` y `afin` ya usaba
  `documentation/adr/`.
- **Mover retroactivamente las decisiones viejas de `outputs/` a BDRs.** Un
  output viejo que decidió algo queda como registro fechado. Si la decisión sigue
  vigente y alguien la necesita, se escribe el BDR y el output lo enlaza.

## Consecuencias

- El scaffold crea `agenda/companies/` y `agenda/deliverables/`, y un
  `documentation/.overview.md` que explica el criterio donde se lo necesita: en
  el momento de guardar un archivo.
- `file-formats.md`, `docs/agents/decisiones.md`, `/wrap-session` y el
  `CLAUDE.md` de AWI cambian para decir lo mismo.
- Cada org se migra aparte, en su repo, con `git mv` en commits sin cambios de
  contenido —para que `git log --follow` siga encontrando cada archivo— y los
  links se corrigen en un commit separado. Esta decisión no migra nada sola.
