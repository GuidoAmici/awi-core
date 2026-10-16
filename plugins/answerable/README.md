# answerable

Una respuesta larga puede tener todo lo que el lector necesita y aun así no decirle
dónde está nada. `answerable` le da forma fija: cinco bloques con encabezado, cada
ítem abierto por su TLDR, preguntas con número fijo, ningún identificador sin enlace ni paráfrasis y todo comando
dirigido a vos listo para pegar.

**Qué querés que haga:** instalarlo y abrir una sesión — no hay configuración.
**Qué obtenés:** respuestas que se contestan con «191. A».
**Por qué vale la pena:** aceptar una de tres propuestas deja de costar un párrafo.

## Instalación

```bash
cd /donde/quieras && \
claude
```

Y adentro de la sesión:

```
/plugin marketplace add GuidoAmici/awi-core
/plugin install answerable@awi
```

## Qué hace

Un hook de `SessionStart` inyecta [`rules/answerable.md`](rules/answerable.md) al
abrir cada sesión. No hay skills, no hay comandos y no hay estado: las reglas rigen
desde el primer turno o no rigen.

Las cuatro reglas son independientes y se aplican juntas:

| Regla | Qué produce |
|---|---|
| Cinco bloques | Qué hice · Qué tenés que saber · Hilos abiertos · Qué propongo · Qué necesito de vos, con número fijo en cada pregunta |
| El TLDR va primero | Leer sólo las negritas alcanza para tener la respuesta entera |
| Ningún identificador viaja desnudo | `#47` siempre viene enlazado, con qué es y por qué se menciona |
| Los comandos se pegan y corren | Un bloque que copiás sin editar ni una ruta |

## Origen

Salió de [AWI](https://github.com/GuidoAmici/awi-core), donde las reglas vivían
dentro del harness y por eso sólo regían en un repo. Acá viajan a cualquier sesión.

## Licencia

MIT.
