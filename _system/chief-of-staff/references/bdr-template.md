# Business Decision Record (BDR) — plantilla y convención

El **BDR** es el equivalente empresarial del ADR. Documenta decisiones de
negocio **costosas de revertir** (pricing, entrada a un mercado, partnerships,
estructura societaria, contratación clave, inversión, discontinuar una línea).
No se usa para decisiones operativas del día a día.

> Regla de oro (igual que el ADR): si la decisión es barata de cambiar, **no**
> merece un BDR. Solo registrás lo que duele revertir.

## Dónde viven

Uno por organización, en paralelo a los ADR técnicos:

```
_data/organizations/<org>/documentation/bdr/
  0001-<slug-en-kebab-case>.md
  0002-<slug>.md
```

- Numeración correlativa de cuatro dígitos por organización (igual que los ADRs).
- Inmutables salvo el campo **Estado**: un BDR no se borra ni se reescribe; si
  se revierte, se crea uno nuevo que lo **supersede** y se marca el viejo.

## Campos del frontmatter (encabezado)

| Campo | Qué captura |
|---|---|
| **Fecha** | Cuándo se tomó (no cuándo se redactó el doc) |
| **Estado** | `Propuesto` · `Aceptado` · `Rechazado` · `Superado por BDR-NNN` |
| **Driver** | Quién impulsa y es dueño de la decisión (una persona) |
| **Aprobó** | Quién tiene la autoridad final (una persona) |
| **Consultados** | Quiénes aportaron input |
| **Informados** | A quién se comunica el resultado |
| **Revisar** | Fecha o disparador para reevaluar (ej. "Q4 2026" o "si churn > 8%") |

`Driver / Aprobó / Consultados / Informados` = roles **DACI**. En decisiones
chicas, Driver y Aprobó pueden ser la misma persona.

---

## Plantilla

```markdown
# BDR-NNN: <título de la decisión en una línea>

**Fecha:** YYYY-MM-DD
**Estado:** Propuesto | Aceptado | Rechazado | Superado por BDR-NNN
**Driver:** <nombre>
**Aprobó:** <nombre>
**Consultados:** <nombres>
**Informados:** <nombres / áreas>
**Revisar:** <fecha o condición disparadora>

## Contexto

Qué situación de negocio forzó la decisión. Hechos, no opiniones: números,
restricciones, presión competitiva, plazos. Por qué *ahora*.

## Decisión

Qué se decidió, en presente y en una frase rotunda. Después el detalle:
alcance, condiciones, límites.

## Impacto económico

Costo, ingreso esperado, inversión comprometida o riesgo cuantificado. Aunque
sea un rango o una estimación gruesa — el punto es que la decisión tenga un
número asociado. "No material" es una respuesta válida y explícita.

## Alternativas descartadas

Cada opción que se consideró y **por qué se descartó**. Esta sección es la que
le da valor al BDR dentro de seis meses: explica qué ya se pensó y no hace
falta volver a discutir.

## Consecuencias

Qué cambia a partir de ahora — lo bueno y lo costoso. Qué se vuelve más difícil.
Qué hay que monitorear. Qué se rompe si la decisión resulta equivocada.
```

---

## Notas de uso en AWI

- Para redactar un BDR podés correr `/mattpocock-skills:grilling` antes: te fuerza a resolver cada
  rama de la decisión, y de ahí sale el contenido de *Alternativas descartadas*.
- Una decisión estratégica suele empezar como un doc suelto en
  `documentation/operaciones/` o `documentation/empresa/` (ej. una estrategia de
  pricing). Cuando se **toma** la decisión, el BDR es el registro permanente; el
  doc de análisis queda como material de respaldo enlazado desde *Contexto*.
- Si una decisión empresarial tiene implicancias técnicas, enlazá el ADR
  correspondiente desde *Consecuencias* (y viceversa).
