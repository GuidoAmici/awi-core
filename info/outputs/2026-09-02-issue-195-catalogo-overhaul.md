# Overhaul de UX/UI de `/catalogo` — los cuatro slices, entregados

**Qué hice:** los cuatro slices del [issue #195](https://github.com/GuidoAmici/newhaze-webapp/issues/195) (el catálogo de newhaze se ve grande, pegado, con las fotos cortadas y sin dónde buscar ni leer la descripción), en cuatro PRs apilados — [#213](https://github.com/GuidoAmici/newhaze-webapp/pull/213) densidad y thumbnail cuadrado, [#214](https://github.com/GuidoAmici/newhaze-webapp/pull/214) búsqueda y filtro con estado en la URL, [#216](https://github.com/GuidoAmici/newhaze-webapp/pull/216) modal de detalle con `long_description`, [#218](https://github.com/GuidoAmici/newhaze-webapp/pull/218) carrito consumer que termina en WhatsApp.
**Qué necesito de vos:** mergear los PRs **en orden S1 → S2 → S3 → S4** (cada uno apunta al anterior y hay que re-apuntarlos a `stg` a medida que bajen), revisar los bloques «Sólo vos» de cada PR, y decidir sobre **`long_description`: hoy ningún producto la tiene cargada**, así que el modal de S3 funciona pero no muestra texto largo hasta que alguien llene esa columna.
**Qué obtenés:** un catálogo denso y mobile-first, con búsqueda sin acentos, filtro por categoría compartible por URL, detalle en modal y un carrito de consumer que termina en un mensaje de WhatsApp — 88 tests nuevos y ninguna decisión de precio ni de RLS movida de lugar.
**Por qué vale la pena:** el patrón viene de `/productos` de afin-webapp, que ya corre en producción en otra app de la misma casa; lo que se portó está probado, y lo que **no** había que portar de él —su catálogo no es responsive— quedó explícitamente excluido y documentado en el código.

---

## Los cuatro PRs

| Slice | PR | Base | Qué resuelve |
|---|---|---|---|
| S1 | [#213](https://github.com/GuidoAmici/newhaze-webapp/pull/213) — grilla densa y thumbnail cuadrado | `stg` | Síntomas 1 (cards grandes y pegadas) y 2 (fotos cortadas) |
| S2 | [#214](https://github.com/GuidoAmici/newhaze-webapp/pull/214) — búsqueda y filtro con estado en la URL | S1 | Las dos piezas que el issue no pedía y la referencia trae |
| S3 | [#216](https://github.com/GuidoAmici/newhaze-webapp/pull/216) — modal de detalle con `long_description` | S2 | Síntomas 3 (falta descripción) y 4 (el botón iba a una landing) |
| S4 | [#218](https://github.com/GuidoAmici/newhaze-webapp/pull/218) — carrito consumer a WhatsApp | S3 | Síntoma 4b (no había cómo juntar varios productos) |

Están **apilados**: el diff de cada uno es solo su propio slice. A medida que S1 mergee, S2 se re-apunta a `stg`, y así.

---

## Las tres decisiones del maintainer, respetadas

Las tomó el 2026-09-02 en el comentario «Referencia elegida y las tres decisiones, resueltas», y no se re-litigaron:

1. **Relación de aspecto cuadrada** — `1/1` con `object-cover` en la card, `object-contain` con padding en el detalle. Implementado tal cual.
2. **Landings por producto: no se generalizan** — el detalle genérico es un modal. `src/app/[producto]/` sigue sirviendo solo los cinco líquidos de la línea pH desde `src/lib/productos-ph.ts`, sin tocarse.
3. **Carrito consumer terminando en WhatsApp** — extensión del canal, no un cobro. Compatible con [ADR-0003](https://github.com/GuidoAmici/newhaze-webapp/blob/stg/docs/adr) §5 (nada de checkout ni cobro en la webapp).

---

## La restricción dura, y cómo se resolvió

**`ProductCard` tenía que seguir siendo server component.** Mezclarle interactividad fue lo que rompió `/catalogo` con un 500 en el preview del [PR #174](https://github.com/GuidoAmici/newhaze-webapp/pull/174) (badges de promo por canal) — y lo atrapó el gate E2E, no los tests unitarios.

La solución no fue convertir la card, sino **invertir quién manda**: el servidor renderiza todas las cards **y todos los cuerpos de detalle**, y se los pasa al componente cliente ya hechos, como nodos opacos. `CatalogBrowser` solo decide **cuáles se muestran**; el chrome del modal solo decide **cuál se abre**. Ninguno los construye.

Consecuencias que importan:

- Ni los precios, ni la lógica de cascada por tier, ni las decisiones de la RLS cruzan al browser. **Lo que un viewer no puede ver, no está en el payload.**
- Las cards siguen dentro del `OrderBuilderProvider`, así que el stepper de cantidad y la escalera May.x leen su contexto igual que antes.
- Es la misma separación de `wholesaler-ladder.tsx`, un escalón más arriba.

Los disparadores que sí viven dentro de la card (`DetailTrigger`, `QtyStepper`) son **client components hijos**, el patrón que la card ya usaba, y **degradan a nada sin su provider** — nunca tiran. Un `throw` ahí sería otra vez un 500 en `/catalogo`; hay tests que lo fijan.

---

## Lo que se portó de afin-webapp, y lo que deliberadamente no

**Se portó** el patrón de interacción: grilla densa, thumbnail cuadrado, `normalize()` con NFD para buscar sin acentos, filtros con estado en la URL, modal con carrusel y relacionados.

**No se portó el CSS.** afin es CSS global con clases planas y paleta naranja; newhaze es Tailwind v4 con tokens `nh-*`. **No se definió ni un color ni un token nuevo** — el color por categoría sale de `src/components/catalog/category.ts`, que sigue siendo su única fuente.

**No se portó su falta de responsive.** En afin, `.products-layout` y `.products-grid` no tienen una sola media query. En newhaze cada breakpoint es deliberado, y el filtro se resolvió con chips que envuelven solos en vez del sidebar de 240px de la referencia — que con tres categorías queda, como el propio issue anticipaba, más vacío que útil.

---

## Cuatro decisiones propias, documentadas en el código

1. **La densidad de la grilla depende del viewer.** consumer/anon va 2 → 3 → 4 columnas; B2B va 1 → 2 → 3. Para un B2B la misma card es además una línea del armador de pedido: a 2 columnas en un teléfono el track queda en ~160px y el stepper deja de ser usable. B2B igual queda más denso que el `md:grid-cols-2` anterior.
2. **`?cat=&sub=` se resuelve también en el servidor.** En la referencia el filtro se resuelve recién al hidratar, así que una URL compartida llega como catálogo completo y salta. Acá el HTML inicial ya viene filtrado — verificado con `curl`.
3. **El detalle se abre con un botón explícito, no con la card entera clickeable.** Esa card ya contiene el link de WhatsApp, el stepper y las flechas de la galería: anidar controles dentro de un `role="button"` es HTML inválido y rompe el teclado. afin puede permitírselo porque su card no tiene controles adentro.
4. **El total del pedido se manda como "estimado".** El mensaje abre una conversación, no cierra una venta.

Además, sobre la referencia: trampa de foco con Tab dentro del modal, foco que vuelve al botón de cerrar al saltar a un relacionado, scroll de fondo bloqueado, y cierre por overlay que distingue `mousedown` de `click` (si no, arrastrar una selección de texto y soltar afuera cerraba el modal).

---

## Qué queda listo para el issue #196

El [issue #196](https://github.com/GuidoAmici/newhaze-webapp/issues/196) (`/catalogo` no distingue lo que ve un interno de lo que ve un cliente) toca la misma card, y el brief pedía no obligar a rehacerla. Lo que dejé preparado:

- **El badge de promo pasó de badge suelto a pila de badges** — una columna en la esquina del thumbnail. Cuando #196 necesite marcar «no vendible» o «inactivo», suma el suyo ahí **sin rehacer el layout ni pelear por la esquina**.
- **La grilla ya es consciente del viewer** (`GRID_BY_VIEWER`), así que #196 tiene dónde colgar una densidad o un tratamiento distinto para el interno sin inventar el mecanismo.
- **Las facetas del filtro se derivan de los items que la RLS devolvió**, no de una lista fija: cuando #196 cambie qué ve un interno, el filtro se ajusta solo y nunca muestra una categoría que daría cero.
- Las columnas `is_salable` / `is_active` de `items` —que son el corazón de #196— **existen y siguen sin pedirse** en `CATALOG_SELECT`. Agregarlas es un cambio de una línea en el mismo lugar donde S3 agregó `long_description` y `variant`.

---

## Verificación

Cada PR pasó `typecheck`, `eslint` sobre sus archivos (exit 0), la suite completa de vitest y `npm run build` antes de abrirse.

**Tests: 366 → 454** (+88 nuevos, 53 archivos, todos verdes).

Y, porque los tests unitarios no atraparon la rotura del #174, **cada slice se probó además contra un servidor de producción real con la Supabase de verdad** (`next start` + `curl`, viewer `anon`):

- `/catalogo` → **HTTP 200**, 17 cards, 17 steppers, 17 botones "Ver detalle", 17 cuerpos de detalle en el payload RSC.
- `/catalogo?cat=medidores` → **200, 4 cards**; `?cat=Medidores` (mayúscula) → 4; `?cat=consumibles` → 12; `?cat=fertilizantes` (inexistente) → **17, cae a "todos", nunca a cero**.
- Chips con los conteos reales del catálogo vivo: Consumibles 12 · Medidores 4 · Merchandising 1 = 17.
- **Ningún 200 se convirtió en 500.**

Un test afirma que el mensaje de WhatsApp no contiene `pagar|pago|checkout|tarjeta|mercadopago`: la regla del ADR-0003 §5 queda fijada por una máquina y no por la memoria de quien revise.

---

## Dos cosas que descubrí y conviene que sepas

**1. `long_description` está vacía en toda la base.** Verificado contra la DB real: ninguno de los 17 productos que ve un `anon` la tiene cargada. El modal de S3 la renderiza bien y omite la sección con gracia cuando falta — pero **hasta que alguien llene esa columna, el detalle no va a mostrar texto largo**. Es una tarea de datos, no de código. Decime si querés que abra un issue para cargarla.

**2. Este working copy lo está usando otro proceso al mismo tiempo.** A mitad del trabajo, el `HEAD` del repo se movió solo a una rama ajena (`feat/flags-vercel-dashboard`, una migración del SDK de Vercel Flags que no tiene nada que ver con #195), y por eso mi rama de S3 nació de la base equivocada — lo detecté y la re-apunté antes de commitear. Esa migración de flags sigue **sin commitear** en el working copy (`.env.example`, `package.json`, `src/flags.ts`, el route handler de discovery): **la dejé intacta y fuera de mis cuatro PRs**, que están acotados a archivos de catálogo. Verificado PR por PR. Pero si hay otra sesión trabajando ahí, conviene que cierre lo suyo antes de que se pisen.
