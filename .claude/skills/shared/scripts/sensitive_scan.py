"""Motor de reglas: qué es material sensible.

Deliberadamente no sabe de git ni importa `subprocess`. Recibe entradas
`(ruta, contenido)` y devuelve hallazgos. Ese corte es lo que permite que la
definición de «sensible» sea **una sola** para sus tres consumidores:

  - `history_audit.py`  — el inventario del historial
  - el hook de pre-commit — la prevención
  - la verificación post-purga — que es el mismo inventario otra vez

Si cada uno tuviera su lista, divergirían, y el hook dejaría pasar exactamente
lo que la auditoría busca. Ver ADR 0014 y el PRD 1 (issue #80).

Las reglas viven en un archivo JSON versionado (`.claude/rules/`), no acá:
agregar un patrón no debe requerir tocar el motor.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

# ── Categorías ───────────────────────────────────────────────────────────────
# La categoría gobierna la severidad. No es una lista plana porque una password
# de una cuenta de prueba y la auditoría de seguridad del código de un cliente
# no merecen la misma respuesta.
#
# Un archivo de reglas puede declarar sus propias categorías con su severidad,
# que es lo que permite usar este motor para algo que no es material sensible —
# el verificador de vocabulario prohibido del PRD 3 (issue #82) lo hace. Si no
# las declara, se asumen éstas.
CREDENCIAL = "credencial"
MATERIAL_DE_CLIENTE = "material-de-cliente"
RUIDO_OPERATIVO = "ruido-operativo"

#: categoría → si bloquea (frente a sólo advertir).
CATEGORIAS_SENSIBLES = {
    CREDENCIAL: True,
    MATERIAL_DE_CLIENTE: True,
    RUIDO_OPERATIVO: False,
}
CATEGORIAS = tuple(CATEGORIAS_SENSIBLES)
BLOQUEANTES = frozenset(c for c, b in CATEGORIAS_SENSIBLES.items() if b)

#: Archivos de reglas, relativos a la raíz de AWI.
REGLAS_SENSIBLES = ".claude/rules/sensitive.json"
REGLAS_VOCABULARIO = ".claude/rules/vocabulario.json"

#: Un blob más grande que esto no se escanea por contenido. El historial completo
#: se recorre en CI en cada push: el motor tiene que ser barato.
MAX_BYTES = 1_000_000

REDACTADO = "«redactado»"


class ReglasInvalidas(ValueError):
    """El archivo de reglas no se puede usar. Falla ruidosamente a propósito."""


@dataclass(frozen=True)
class Regla:
    nombre: str
    categoria: str
    descripcion: str
    remedio: str
    #: Lo declara la categoría en el archivo de reglas, no el código.
    bloquea: bool = True
    ruta: re.Pattern | None = None
    contenido: re.Pattern | None = None
    #: Rutas donde la regla no aplica. Necesario y no cosmético: los fixtures de
    #: test contienen credenciales a propósito, y este mismo archivo de reglas
    #: contiene los patrones que busca.
    excepto_rutas: tuple[re.Pattern, ...] = ()
    #: Coincidencias que son placeholder y no secreto (`${VAR}`, `YOUR_TOKEN`).
    excepto_contenido: re.Pattern | None = None

    def aplica_a(self, ruta: str) -> bool:
        if any(x.search(ruta) for x in self.excepto_rutas):
            return False
        return self.ruta is None or bool(self.ruta.search(ruta))


@dataclass(frozen=True)
class Entrada:
    """Un archivo a evaluar. `contenido=None` cuando no se pudo leer.

    Un objeto binario, o uno más grande que `MAX_BYTES`, entra con contenido
    `None` y sólo se evalúa por su ruta. Es una limitación real y explícita:
    una credencial dentro de un `.zip` no la ve este motor.
    """

    ruta: str
    contenido: str | None = None


@dataclass(frozen=True)
class Hallazgo:
    ruta: str
    regla: str
    categoria: str
    remedio: str
    bloquea: bool = True
    linea: int | None = None
    evidencia: str = ""
    #: Contexto del consumidor: un blob del historial trae su commit acá.
    origen: str = ""

    def __str__(self) -> str:
        donde = f"{self.ruta}:{self.linea}" if self.linea else self.ruta
        sufijo = f" — {self.evidencia}" if self.evidencia else ""
        return f"[{self.categoria}] {donde} ({self.regla}){sufijo}"


@dataclass
class Reporte:
    hallazgos: list[Hallazgo] = field(default_factory=list)
    #: Las categorías del conjunto de reglas usado, en orden de declaración. Van
    #: en el reporte y no derivadas de los hallazgos, para que una categoría sin
    #: hallazgos aparezca en cero en vez de desaparecer.
    categorias: tuple[str, ...] = CATEGORIAS

    @property
    def bloqueantes(self) -> list[Hallazgo]:
        return [h for h in self.hallazgos if h.bloquea]

    def por_categoria(self) -> dict[str, int]:
        conteo = {c: 0 for c in self.categorias}
        for h in self.hallazgos:
            conteo[h.categoria] = conteo.get(h.categoria, 0) + 1
        return conteo

    def rutas(self) -> list[str]:
        """Rutas distintas con hallazgos, ordenadas. Es lo que consume la purga."""
        return sorted({h.ruta for h in self.hallazgos})

    def __bool__(self) -> bool:
        return bool(self.hallazgos)


# ── Carga de reglas ──────────────────────────────────────────────────────────

def _compilar(patron: str | None, campo: str, nombre: str) -> re.Pattern | None:
    if patron is None:
        return None
    try:
        return re.compile(patron)
    except re.error as e:
        raise ReglasInvalidas(f"regla «{nombre}»: {campo} no es una regex válida: {e}") from e


def cargar_reglas(archivo: str | Path) -> list[Regla]:
    """Lee el archivo de reglas versionado.

    Falla ruidosamente ante un archivo ausente, mal formado o con una categoría
    desconocida. Una auditoría que corre con cero reglas porque no encontró su
    archivo reporta «todo limpio», que es la peor respuesta posible.
    """
    archivo = Path(archivo)
    try:
        crudo = json.loads(archivo.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise ReglasInvalidas(f"no existe el archivo de reglas: {archivo}") from e
    except json.JSONDecodeError as e:
        raise ReglasInvalidas(f"{archivo} no es JSON válido: {e}") from e

    entradas = crudo.get("reglas")
    if not isinstance(entradas, list) or not entradas:
        raise ReglasInvalidas(f"{archivo} no declara ninguna regla en «reglas»")

    categorias = crudo.get("categorias") or CATEGORIAS_SENSIBLES
    if not isinstance(categorias, dict):
        raise ReglasInvalidas(f"{archivo}: «categorias» tiene que ser un objeto")
    severidad = {
        nombre: bool(cfg.get("bloquea", True)) if isinstance(cfg, dict) else bool(cfg)
        for nombre, cfg in categorias.items()
    }

    reglas: list[Regla] = []
    vistos: set[str] = set()
    for cruda in entradas:
        nombre = cruda.get("nombre")
        if not nombre:
            raise ReglasInvalidas(f"{archivo}: hay una regla sin «nombre»")
        if nombre in vistos:
            raise ReglasInvalidas(f"{archivo}: regla duplicada «{nombre}»")
        vistos.add(nombre)

        categoria = cruda.get("categoria")
        if categoria not in severidad:
            raise ReglasInvalidas(
                f"regla «{nombre}»: categoría «{categoria}» desconocida; "
                f"las válidas son {', '.join(severidad)}"
            )

        ruta = _compilar(cruda.get("ruta"), "ruta", nombre)
        contenido = _compilar(cruda.get("contenido"), "contenido", nombre)
        if ruta is None and contenido is None:
            raise ReglasInvalidas(f"regla «{nombre}»: no declara ni «ruta» ni «contenido»")

        reglas.append(
            Regla(
                nombre=nombre,
                categoria=categoria,
                descripcion=cruda.get("descripcion", ""),
                remedio=cruda.get("remedio", ""),
                bloquea=severidad[categoria],
                ruta=ruta,
                contenido=contenido,
                excepto_rutas=tuple(
                    _compilar(p, "excepto_rutas", nombre)
                    for p in cruda.get("excepto_rutas", [])
                ),
                excepto_contenido=_compilar(
                    cruda.get("excepto_contenido"), "excepto_contenido", nombre
                ),
            )
        )
    return reglas


# ── Escaneo ──────────────────────────────────────────────────────────────────

def _redactar(linea: str, match: re.Match, categoria: str) -> str:
    """Fragmento de evidencia sin el secreto adentro.

    Un reporte de credenciales que imprime las credenciales es otra fuga: la
    auditoría corre en CI y su salida queda en los logs del workflow.
    """
    texto = linea.strip()
    if categoria == CREDENCIAL:
        texto = (texto[: match.start() - (len(linea) - len(linea.lstrip()))].lstrip() + REDACTADO)
        texto = texto.strip() or REDACTADO
    return texto[:120]


def escanear(entradas, reglas: list[Regla]) -> Reporte:
    """Evalúa cada entrada contra cada regla. Puro: sin disco, sin git.

    Una regla con `ruta` y `contenido` exige que coincidan las dos. Con sólo
    `ruta`, alcanza la ruta — y es la única clase de regla que puede decidir
    sobre una entrada cuyo contenido no se pudo leer.
    """
    reporte = Reporte(categorias=tuple(dict.fromkeys(r.categoria for r in reglas)))
    for entrada in entradas:
        contenido = entrada.contenido
        if contenido is not None and (
            len(contenido) > MAX_BYTES or "\x00" in contenido[:8192]
        ):
            contenido = None  # binario o demasiado grande: sólo por ruta

        aplicables = [r for r in reglas if r.aplica_a(entrada.ruta)]
        for regla in aplicables:
            if regla.contenido is None:
                reporte.hallazgos.append(
                    Hallazgo(
                        ruta=entrada.ruta,
                        regla=regla.nombre,
                        categoria=regla.categoria,
                        remedio=regla.remedio,
                        bloquea=regla.bloquea,
                        origen=getattr(entrada, "origen", ""),
                    )
                )
                continue
            if contenido is None:
                continue
            for n, linea in enumerate(contenido.splitlines(), start=1):
                m = regla.contenido.search(linea)
                if not m:
                    continue
                if regla.excepto_contenido and regla.excepto_contenido.search(m.group(0)):
                    continue  # placeholder, no secreto
                reporte.hallazgos.append(
                    Hallazgo(
                        ruta=entrada.ruta,
                        regla=regla.nombre,
                        categoria=regla.categoria,
                        remedio=regla.remedio,
                        bloquea=regla.bloquea,
                        linea=n,
                        evidencia=_redactar(linea, m, regla.categoria),
                        origen=getattr(entrada, "origen", ""),
                    )
                )
                break  # una coincidencia por archivo y regla alcanza
    return reporte
