"""Integridad del registro de decisiones.

Es el test que hizo segura la renumeración del [ADR 0018]: se corrió antes de
cambiar los números —donde fallaba, con cuatro colisiones— y después. Sin él, la
renumeración habría sido un movimiento de archivos verificado a ojo.

Lo que verifica es lo que hace citable un ADR: que un número identifique
exactamente una decisión, y que un enlace entre ADRs resuelva a un archivo que
existe.
"""

import re

import pytest

from paths import AWI_ROOT

ADR_DIR = AWI_ROOT / "docs/adr"

#: `0009-manifiestos-json-en-lugar-de-submodulos.md`
NOMBRE = re.compile(r"^(\d{4})-([a-z0-9-]+)\.md$")

#: Enlaces markdown a otro ADR, con o sin ruta: `](0009-...)`, `](adr/0009-...)`,
#: `](../blob/main/docs/adr/0009-...)`.
ENLACE = re.compile(r"\]\(([^)]*?(\d{4}-[a-z0-9-]+\.md))(?:#[^)]*)?\)")


def adrs():
    return sorted(p for p in ADR_DIR.glob("*.md") if NOMBRE.match(p.name))


def test_hay_adrs():
    assert adrs(), f"no se encontró ningún ADR en {ADR_DIR}"


def test_todo_archivo_del_directorio_sigue_la_convencion():
    invalidos = [p.name for p in ADR_DIR.glob("*.md") if not NOMBRE.match(p.name)]
    assert not invalidos, f"nombres que no siguen NNNN-titulo-en-kebab.md: {invalidos}"


def test_un_numero_identifica_exactamente_una_decision():
    """La regresión del ADR 0018. Falla con las colisiones de 0005 a 0008."""
    por_numero: dict[str, list[str]] = {}
    for p in adrs():
        por_numero.setdefault(NOMBRE.match(p.name).group(1), []).append(p.name)

    colisiones = {n: v for n, v in por_numero.items() if len(v) > 1}
    assert not colisiones, f"números con más de una decisión: {colisiones}"


def test_los_numeros_no_tienen_huecos():
    """Un hueco significa que un ADR se borró sin registrar qué pasó con él."""
    numeros = sorted(int(NOMBRE.match(p.name).group(1)) for p in adrs())
    esperados = list(range(numeros[0], numeros[-1] + 1))
    assert numeros == esperados, f"faltan: {sorted(set(esperados) - set(numeros))}"


def test_todo_enlace_entre_adrs_resuelve():
    """Un registro con enlaces colgantes es el patrón de residuo del ADR 0013."""
    existentes = {p.name for p in adrs()}
    colgantes = []
    for p in adrs():
        for _, destino in ENLACE.findall(p.read_text(encoding="utf-8")):
            if destino not in existentes:
                colgantes.append(f"{p.name} → {destino}")
    assert not colgantes, "enlaces a ADRs que no existen:\n  " + "\n  ".join(colgantes)


def test_los_enlaces_desde_la_capa_de_contexto_resuelven():
    """CONTEXT.md, el README y las skills citan ADRs por ruta: si el número cambia
    y la referencia no, el lector queda sin la decisión que buscaba."""
    existentes = {p.name for p in adrs()}
    fuentes = [AWI_ROOT / "CONTEXT.md", AWI_ROOT / "README.md"]
    fuentes += sorted(AWI_ROOT.glob(".claude/skills/*/SKILL.md"))

    colgantes = []
    for f in fuentes:
        if not f.is_file():
            continue
        for _, destino in ENLACE.findall(f.read_text(encoding="utf-8")):
            if destino not in existentes:
                colgantes.append(f"{f.relative_to(AWI_ROOT)} → {destino}")
    assert not colgantes, "referencias a ADRs inexistentes:\n  " + "\n  ".join(colgantes)


def test_todo_adr_tiene_un_titulo_h1():
    sin_titulo = [
        p.name
        for p in adrs()
        if not p.read_text(encoding="utf-8").lstrip().startswith("# ")
    ]
    assert not sin_titulo, f"ADRs sin título H1: {sin_titulo}"


def test_no_quedan_duplicados_en_ingles_de_una_decision_en_castellano():
    """Los pares que el ADR 0018 eliminó, aseverados por su ausencia."""
    eliminados = (
        "0007-awi-core-as-source-of-truth.md",
        "0008-agent-discovery-over-employees-registry.md",
    )
    presentes = [n for n in eliminados if (ADR_DIR / n).exists()]
    assert not presentes, f"volvieron los duplicados en inglés: {presentes}"


def test_el_mapeo_de_la_renumeracion_esta_registrado():
    """Los mensajes de commit no se pueden actualizar: si el mapeo no está escrito,
    una referencia histórica deja de ser resoluble."""
    mapeo = ADR_DIR / "0018-numeracion-e-idioma-del-registro-de-decisiones.md"
    assert mapeo.is_file()
    texto = mapeo.read_text(encoding="utf-8")
    for viejo in (
        "0005-standard-git-flow-over-tool-identity-branches.md",
        "0006-user-org-relationship-lives-in-user-space.md",
        "0007-awi-core-as-source-of-truth.md",
        "0008-agent-discovery-over-employees-registry.md",
    ):
        assert viejo in texto, f"el mapeo no dice qué pasó con {viejo}"
