---
fecha: 2026-09-04
issue: GuidoAmici/newhaze-webapp#255
pr: GuidoAmici/newhaze-webapp#257
adr: ADR-0025 (PR #256)
agente: frontend-developer
affects: docs/adr/0025-home-shell-estatico-visitante-despues-de-la-hidratacion.md
---

# Home de New Haze: shell estático desde el CDN

## Qué se entregó

PR [#257](https://github.com/GuidoAmici/newhaze-webapp/pull/257) contra `stg`, rama
`feat/255-home-shell-estatico`. 25 archivos, +1029 / −189. Sin migraciones.

La home y cuatro páginas públicas de marketing (`/vision`, `/phmetro-v3`,
`/privacidad`, `/terminos`) pasan a servirse prerenderizadas desde el CDN, con ISR
de 60 s. La CTA contextual arranca en un estado neutro y se resuelve en el cliente
contra `/api/cta-visitor`, que por dentro es el mismo `resolveVisitorFromSession()`
que `/revendedores` sigue usando en SSR (ADR-0008 intacto).

## Lo que había que entender antes de tocar nada

**El culpable no era sólo la home.** El brief decía —con razón— que lo que ataba la
página a una función era `resolveVisitorFromSession()` en su render. Pero medido, el
build mostraba las **22 rutas del sitio** como `ƒ (Dynamic)`, incluidas `/privacidad`
y `/terminos`, que no tienen ni datos ni sesión. La causa común es el **root layout**:
evalúa cinco feature flags, resuelve la vista previa de admin y monta el gate del quiz
de segmentación, todo leyendo el request.

Eso descartaba la solución obvia (sacar la lectura de `page.tsx` y listo) y abría tres
caminos: partir el root layout en dos por route groups —que convierte la navegación
home → catálogo en una recarga completa, justo el camino del CTA principal—, mover las
tres lecturas del layout al cliente para toda la app, o `export const dynamic =
"force-static"` en las páginas que tienen que ser estáticas, que neutraliza lo que el
layout lee **sólo en esa ruta**. Se eligió la tercera: quirúrgica, sin tocar el
comportamiento de las 17 rutas dinámicas y sin romper la navegación cliente.

**El costo de `force-static` es que no avisa.** No falla si alguien mete un `cookies()`
en el árbol server: hace que devuelva vacío. La página seguiría buildeando y hornearía
"visitante anónimo" en el HTML de todos — el flash que #82 prohíbe, ahora servido desde
el CDN. De ahí que el guardarraíl del criterio 9 no sea un extra sino la mitad del
trabajo.

## Los números

Preview vs producción, navegador real (iPhone 390×844, 4G, CPU 4× lenta), 10 cargas
de cada lado:

| | antes (prod, dinámica) | después (preview, estática) |
|---|---|---|
| TTFB | 38–46 ms · media 41 | 39–43 ms · media 41 |
| **FCP** | **692–2956 ms** · media 985 | **536–804 ms** · media 625 |
| load | 1536–3810 ms · media 1854 | 1884–2303 ms · media 2069 |

**En una respuesta streameada el cold start no cae en el TTFB, cae en el FCP.** El
shell se flushea enseguida y el contenido llega cuando el server terminó de renderizar.
Por eso prod muestra TTFB de 41 ms con FCP de 2956 ms en la carga fría. Ese peor caso
es el síntoma reportado en el issue, y es el que desaparece: **FCP máximo 2956 → 804 ms
(−73 %)**, load máximo 3810 → 2303 ms (−40 %).

10 peticiones consecutivas al HTML del preview: **10/10 desde el CDN**, todas con
`x-nextjs-prerender: 1`. Descontada la conexión, el servidor tarda 180–215 ms; el
control en el mismo deployment (`/revendedores`, que sigue dinámica) tarda 300–392 ms
aun con la lambda caliente.

**No se pudo reproducir a demanda el pico de 2–3 s** que documentó el triage: Fluid
Compute mantiene las lambdas del preview más calientes de lo que sugiere el issue. El
argumento que sostiene la entrega no es estadístico sino estructural — la home ya no
invoca una función, y una ruta que no invoca una función no puede pagar un cold start.
Un muestreo puede no pegarle a un pico intermitente; la ausencia de la función, no.

El JS de la app crece 2 KB (258 → 260 KB), medido por origen. Los +30 KB que aparecen
en el total del preview son la toolbar de Vercel, que en producción no existe.

## Dos cosas que aparecieron midiendo

**1. El quiz de segmentación se rompía en silencio.** Con la home prerenderizada su HTML
es idéntico para todos, así que el gate de #120 (montado en el root layout) no puede
decidir ahí si a alguien le toca. Y la home es exactamente donde aterriza un registro
recién verificado: `/auth/callback` redirige a `/`. O sea, los usuarios nuevos de la
campaña —los que #120 existe para segmentar— se quedaban sin quiz hasta navegar a otra
página. Ningún test lo detectaba.

Se arregló moviendo la decisión a `/api/segment-quiz`: la misma regla pura, el mismo
kill switch, el mismo fast-path por cookie. Efecto lateral bueno: el root layout deja de
pagar un `getClaims()` + una query a `profiles` en el SSR de **todas** las páginas del
sitio, y el overlay ahora aparece al establecerse la sesión sin esperar un refresh.

**2. `catalog.ts` mezclaba la lectura pública con la del viewer.** El guardarraíl lo
encontró solo: cualquier consumidor del catálogo público arrastraba
`@/lib/supabase/server` a su grafo de imports. No era ruido — es la frontera entre lo
cacheable y lo que **nunca** se puede cachear por URL (mezclar tiers entre sesiones es
una fuga de precios), y no se veía en ningún import. `fetchCatalogForViewer` salió a
`catalog.server.ts` sin una línea distinta, verificado con `diff` byte a byte contra
`origin/stg`.

## Consecuencias que necesitan decisión humana

Quedaron como ítems "Sólo vos" del PR:

- **Los flags se hornean.** En las cinco rutas estáticas un toggle del dashboard tarda
  hasta 60 s (el ISR) y el override por sesión de la Toolbar de Vercel no las alcanza.
  Para los kill switches (`users`, `google-signin`) 60 s parece tolerable, pero es una
  decisión de producto, no técnica.
- **La barra de vista previa de admin no aparece en las rutas estáticas**, mientras que
  la CTA de la home sí honra la cookie de preview (la resuelve el route handler, que lee
  el request). Un admin en modo vista previa ve la home con la identidad de otro y sin el
  aviso. La barra vuelve en cualquier otra página. Si no se tolera, mudarla al cliente es
  un PR propio.

Ninguna de las dos está en las consecuencias del ADR-0025, que todavía no mergea (#256):
conviene agregarlas ahí antes.

## Un tercer hallazgo: una carrera que ya existía en los E2E

Al hacer que el gate del quiz resuelva apenas se establece la sesión, quedó al
descubierto una carrera preexistente en `auth.spec.ts`. El overlay es un diálogo
modal y Radix le pone `aria-hidden` a todo lo que queda afuera, así que
`getByRole` no encuentra el header aunque esté ahí y visible — y el
`toHaveCount(0)` de "Acceder" pasaba **por el motivo equivocado**. Antes la
aserción le ganaba la carrera al overlay (que llegaba recién con el
`router.refresh()` del login); ahora no. El comentario del archivo, que decía que
el overlay no oculta el header, sólo era cierto para los clicks.

Se arregló buscando por DOM en vez de por rol, y `loginViaAuthModal` ahora espera
la respuesta de `/api/segment-quiz` antes de devolver el control: el estado queda
determinístico en vez de depender de quién gana la carrera.

## Estado final

Los 12 checks de la Stg CI en verde, incluido el gate de Playwright contra el
preview: **499 unit + 19 E2E, 0 fallas**, 3 skips que son los `test.skip`
condicionales que ya existían. PR abierto esperando review.

## Fuera de alcance, respetado

No se prendió `cacheComponents` ni hizo falta. No se tocó RLS, migraciones, el bundle,
las imágenes, `/revendedores`, `/cuenta/*` ni el Área de empleados. `/pack-ph-v1` quedó
dinámica a propósito: muestra precios por tier del viewer.
