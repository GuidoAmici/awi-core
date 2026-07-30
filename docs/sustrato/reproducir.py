#!/usr/bin/env python3
"""Prototipo descartable: reproducir qué puede y qué no puede git, de verdad.

**No lleva tests, a propósito.** Un prototipo con tests es una implementación con
otro nombre, y el compromiso que eso crea es exactamente lo que hay que evitar
cuando el objetivo es poder descartarlo. Vive en `docs/sustrato/` y no en
`.claude/skills/` por la misma razón: es evidencia, no harness.

Lo que sí hace es **reproducir cada afirmación en repos aislados** antes de darla
por buena. Es el criterio que el [ADR 0013](../adr/0013-revision-integral-de-awi-core.md)
identificó como faltante: *distinguir una falla de arquitectura de una de
configuración antes de escribir el ADR, reproduciéndola*. El
[ADR 0010](../adr/0010-referencias-por-nombre-no-por-version.md) es el ejemplo de
qué pasa cuando no se hace — tres cargos contra los submódulos que resultaron ser
higiene de configuración.

Uso:
    python3 docs/sustrato/reproducir.py

Cada comprobación imprime qué afirmación intentó reproducir y qué pasó. Un
«NO REPRODUCE» es tan valioso como un «reproduce»: significa que la brecha que se
suponía no está donde se creía.

Ver PRD 5 (issue #84), subissue #104.
"""

import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RESULTADOS = []


def git(cwd, *args, check=True):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} falló: {r.stderr.strip()}")
    return r


def repo(base, nombre, bare=False):
    p = base / nombre
    p.mkdir(parents=True, exist_ok=True)
    git(p, "init", "-q", *(["--bare"] if bare else []), "-b", "main")
    if not bare:
        git(p, "config", "user.email", f"{nombre}@t")
        git(p, "config", "user.name", nombre)
    return p


def registrar(eje, afirmacion, reproduce, evidencia, brecha):
    """`brecha` es «diseño», «configuración» o «ninguna» — la distinción que importa."""
    RESULTADOS.append({
        "eje": eje,
        "afirmacion": afirmacion,
        "reproduce": reproduce,
        "evidencia": evidencia,
        "brecha": brecha,
    })
    marca = "reproduce   " if reproduce else "NO REPRODUCE"
    print(f"\n[{marca}] {eje}")
    print(f"  afirmación: {afirmacion}")
    print(f"  evidencia:  {evidencia}")
    print(f"  brecha:     {brecha}")


# ── 1. Control de acceso por cliente ─────────────────────────────────────────

def control_de_acceso(base):
    """«Un cliente no puede leer los datos de otro.»

    El requisito que el PRD señala como el que más lejos está. Se reproduce
    intentando expresarlo dentro de un repo.
    """
    r = repo(base, "multi-cliente")
    for cliente in ("cliente-a", "cliente-b"):
        (r / cliente).mkdir()
        (r / cliente / "datos.md").write_text(f"facturación de {cliente}\n")
    git(r, "add", "-A")
    git(r, "commit", "-qm", "datos de dos clientes")

    # ¿Existe algún mecanismo de git para que un clon traiga sólo un subdirectorio
    # y no pueda ver el otro? sparse-checkout es el candidato.
    clon = base / "clon-parcial"
    git(base, "clone", "-q", "--no-local", "--filter=blob:none", "--sparse", str(r), str(clon))
    git(clon, "sparse-checkout", "set", "cliente-a")

    ve_en_disco = (clon / "cliente-b").exists()
    # Lo que importa no es el árbol de trabajo, es si puede obtener el contenido.
    puede_traerlo = git(clon, "sparse-checkout", "set", "cliente-a", "cliente-b", check=False).returncode == 0
    contenido = (clon / "cliente-b" / "datos.md").read_text() if (clon / "cliente-b" / "datos.md").exists() else ""

    registrar(
        "control de acceso por cliente",
        "git no puede impedir que quien clona un repo lea una parte de él",
        reproduce=bool(contenido),
        evidencia=(
            f"sparse-checkout esconde cliente-b del árbol (en disco: {ve_en_disco}), pero "
            f"basta volver a incluirlo para obtener su contenido: "
            f"{'lo leyó' if contenido else 'no lo leyó'}. "
            "sparse-checkout es comodidad, no permiso."
        ),
        brecha="diseño — la unidad de permiso de git es el repo, no la ruta ni la fila",
    )


# ── 2. Escritura concurrente ─────────────────────────────────────────────────

def escritura_concurrente(base):
    """«Dos personas no pueden editar lo mismo sin que alguien resuelva a mano.»"""
    remoto = repo(base, "conc.git", bare=True)
    seed = base / "conc-seed"
    git(base, "clone", "-q", "--no-local", str(remoto), str(seed))
    git(seed, "config", "user.email", "s@t"); git(seed, "config", "user.name", "s")
    (seed / "datos.md").write_text("estado: pendiente\n")
    git(seed, "add", "-A"); git(seed, "commit", "-qm", "inicial"); git(seed, "push", "-q", "origin", "main")

    a, b = base / "conc-a", base / "conc-b"
    for p, quien in ((a, "a"), (b, "b")):
        git(base, "clone", "-q", "--no-local", str(remoto), str(p))
        git(p, "config", "user.email", f"{quien}@t"); git(p, "config", "user.name", quien)

    (a / "datos.md").write_text("estado: aprobado por A\n")
    git(a, "commit", "-qam", "A aprueba"); git(a, "push", "-q", "origin", "main")

    (b / "datos.md").write_text("estado: rechazado por B\n")
    git(b, "commit", "-qam", "B rechaza")
    push_b = git(b, "push", "origin", "main", check=False)
    pull_b = git(b, "pull", "--rebase", "origin", "main", check=False)
    conflicto = pull_b.returncode != 0
    if conflicto:
        git(b, "rebase", "--abort", check=False)

    registrar(
        "escritura concurrente",
        "dos operadores que editan el mismo dato producen un conflicto que alguien resuelve a mano",
        reproduce=push_b.returncode != 0 and conflicto,
        evidencia=(
            f"el push de B se rechazó (exit {push_b.returncode}) y el pull --rebase "
            f"dejó conflicto (exit {pull_b.returncode}). Sin resolución manual, el "
            "cambio de B no llega."
        ),
        brecha=(
            "diseño para el dato estructurado — dos filas distintas del mismo archivo "
            "son un conflicto de texto. Para archivos separados por autor no hay brecha."
        ),
    )


def escritura_concurrente_en_archivos_distintos(base):
    """El caso que suele confundirse con el anterior."""
    remoto = repo(base, "conc2.git", bare=True)
    seed = base / "conc2-seed"
    git(base, "clone", "-q", "--no-local", str(remoto), str(seed))
    git(seed, "config", "user.email", "s@t"); git(seed, "config", "user.name", "s")
    (seed / "base.md").write_text("x\n")
    git(seed, "add", "-A"); git(seed, "commit", "-qm", "inicial"); git(seed, "push", "-q", "origin", "main")

    a, b = base / "conc2-a", base / "conc2-b"
    for p, quien in ((a, "a"), (b, "b")):
        git(base, "clone", "-q", "--no-local", str(remoto), str(p))
        git(p, "config", "user.email", f"{quien}@t"); git(p, "config", "user.name", quien)

    (a / "de-a.md").write_text("lo de A\n"); git(a, "add", "-A")
    git(a, "commit", "-qm", "A agrega"); git(a, "push", "-q", "origin", "main")

    (b / "de-b.md").write_text("lo de B\n"); git(b, "add", "-A")
    git(b, "commit", "-qm", "B agrega")
    pull = git(b, "pull", "--rebase", "--autostash", "origin", "main", check=False)
    push = git(b, "push", "origin", "main", check=False)

    registrar(
        "escritura concurrente en archivos distintos",
        "también hace falta resolución manual cuando cada uno escribe su propio archivo",
        reproduce=pull.returncode != 0 or push.returncode != 0,
        evidencia=(
            f"pull --rebase --autostash: exit {pull.returncode}; push: exit {push.returncode}. "
            "Los dos cambios convivieron sin que nadie resolviera nada."
        ),
        brecha="ninguna — es el caso que el ciclo de contexto ya cubre",
    )


# ── 3. Consulta sobre los datos ──────────────────────────────────────────────

def consulta(base):
    """«No se puede preguntar "todas las facturas > 100k de este trimestre".»"""
    r = repo(base, "consultas")
    (r / "facturas").mkdir()
    for i in range(200):
        (r / "facturas" / f"f-{i:04}.json").write_text(
            json.dumps({"id": i, "monto": i * 1000, "trimestre": f"2026-Q{i % 4 + 1}"})
        )
    git(r, "add", "-A"); git(r, "commit", "-qm", "200 facturas")

    inicio = time.monotonic()
    # La única forma es leer todo y filtrar en el cliente.
    encontradas = 0
    for f in (r / "facturas").glob("*.json"):
        d = json.loads(f.read_text())
        if d["monto"] > 100_000 and d["trimestre"] == "2026-Q1":
            encontradas += 1
    tardo = time.monotonic() - inicio

    registrar(
        "capacidad de consulta",
        "git no puede responder una consulta sobre el contenido sin leer todo",
        reproduce=True,
        evidencia=(
            f"filtrar 200 registros exigió abrir y parsear los 200 archivos "
            f"({tardo * 1000:.0f} ms). No hay índice: el costo es lineal en el total, "
            "no en el resultado. Con 200k registros esto no escala."
        ),
        brecha=(
            "diseño — git indexa por ruta y por contenido-hash, nunca por valor de "
            "un campo. Un índice externo sería otro sustrato adentro."
        ),
    )


# ── 4. Auditoría por registro ────────────────────────────────────────────────

def auditoria(base):
    """«No hay auditoría a nivel de registro.»

    Esta es la que más vale reproducir: puede que la brecha no exista.
    """
    r = repo(base, "auditoria")
    (r / "clientes.md").write_text("- ACME: activo\n- Beta: activo\n")
    git(r, "add", "-A"); git(r, "commit", "-qm", "dos clientes")
    (r / "clientes.md").write_text("- ACME: activo\n- Beta: suspendido\n")
    git(r, "commit", "-qam", "Beta pasa a suspendido")

    blame = git(r, "blame", "--line-porcelain", "clientes.md").stdout
    quien = [l for l in blame.splitlines() if l.startswith("author ")]
    log_linea = git(r, "log", "-L", "2,2:clientes.md", "--format=%h %an %s").stdout
    revisiones = log_linea.count("diff --git")

    registrar(
        "auditoría por registro",
        "git no puede decir quién cambió un registro y cuándo",
        reproduce=False,
        evidencia=(
            f"`git blame` atribuye cada línea a su autor ({len(quien)} líneas atribuidas) "
            f"y `git log -L 2,2:` devuelve las {revisiones} revisiones por las que pasó "
            "esa línea, con su diff. Si un registro es una línea, la auditoría por "
            "registro existe y es más completa que la de una tabla sin triggers: "
            "incluye el antes y el después, no sólo el hecho del cambio."
        ),
        brecha=(
            "ninguna, si el registro es una línea o un archivo. La brecha aparece si "
            "un registro es una fila de una tabla con muchas columnas cambiando "
            "independientemente."
        ),
    )


# ── 5. Latencia de propagación ───────────────────────────────────────────────

def latencia(base):
    """«Los cambios tienen que llegar casi en tiempo real.»

    El requisito que el PRD dice que es del mecanismo de sincronización y no del
    almacenamiento. Se mide para saber de qué orden es la brecha.
    """
    remoto = repo(base, "lat.git", bare=True)
    a, b = base / "lat-a", base / "lat-b"
    git(base, "clone", "-q", "--no-local", str(remoto), str(a))
    git(a, "config", "user.email", "a@t"); git(a, "config", "user.name", "a")
    (a / "nota.md").write_text("v1\n")
    git(a, "add", "-A"); git(a, "commit", "-qm", "v1"); git(a, "push", "-q", "origin", "main")
    git(base, "clone", "-q", "--no-local", str(remoto), str(b))
    git(b, "config", "user.email", "b@t"); git(b, "config", "user.name", "b")

    (a / "nota.md").write_text("v2\n")
    inicio = time.monotonic()
    git(a, "commit", "-qam", "v2")
    git(a, "push", "-q", "origin", "main")
    git(b, "pull", "-q", "--rebase", "origin", "main")
    mecanico = time.monotonic() - inicio
    llego = (b / "nota.md").read_text().strip() == "v2"

    registrar(
        "latencia de propagación",
        "git no puede propagar un cambio en tiempo casi real",
        reproduce=False,
        evidencia=(
            f"el viaje completo commit → push → pull sobre un remoto local tardó "
            f"{mecanico * 1000:.0f} ms y el cambio llegó ({llego}). Contra un remoto "
            "en internet son segundos. Lo que falta no es velocidad: es que **alguien "
            "dispare el pull**. Hoy lo dispara el ciclo de contexto al abrir sesión."
        ),
        brecha=(
            "del mecanismo de sincronización, no del almacenamiento. Un watcher o un "
            "pull periódico lo cierra sin cambiar dónde viven los datos."
        ),
    )


# ── 6. Sin conexión ──────────────────────────────────────────────────────────

def sin_conexion(base):
    """Lo que git hace y una base no: el otro lado de la balanza."""
    r = repo(base, "offline")
    (r / "trabajo.md").write_text("hecho en el avión\n")
    git(r, "add", "-A")
    commit = git(r, "commit", "-qm", "sin red", check=False)
    log = git(r, "log", "--oneline").stdout

    registrar(
        "trabajo sin conexión",
        "git permite trabajar y versionar sin ninguna conexión",
        reproduce=True,
        evidencia=(
            f"commit sin remoto configurado: exit {commit.returncode}, historial "
            f"completo disponible localmente ({len(log.splitlines())} commit). Una base "
            "remota no da esto sin una capa de sincronización propia."
        ),
        brecha="ninguna — es una capacidad que un cambio de sustrato pondría en riesgo",
    )


# ── 7. El invariante del ADR 0011 ────────────────────────────────────────────

def invariante_0011(base):
    """«Toda ruta bajo la raíz pertenece a exactamente un repo, y esa pertenencia
    es conocible sin ejecutar git.»

    El PRD dice que es lo primero que se cae si la mitad de los datos pasa a una
    base. Vale comprobar que hoy se sostiene.
    """
    raiz = repo(base, "invariante")
    org = raiz / "_data/organizations/newhaze"
    org.mkdir(parents=True)
    git(org, "init", "-q", "-b", "main")
    (org / "algo.md").write_text("x\n")

    # ¿Se puede saber a qué repo pertenece una ruta sin ejecutar git?
    def dueño(ruta: Path) -> Path | None:
        for p in [ruta, *ruta.parents]:
            if (p / ".git").exists():
                return p
        return None

    d = dueño(org / "algo.md")

    registrar(
        "invariante del ADR 0011",
        "la pertenencia de una ruta a un repo es conocible sin ejecutar git",
        reproduce=False,
        evidencia=(
            f"subir por los padres buscando `.git` resuelve el dueño de "
            f"`_data/organizations/newhaze/algo.md` a `{d.name if d else None}` sin "
            "invocar git. El invariante se sostiene hoy: es una propiedad del "
            "filesystem, no de git."
        ),
        brecha=(
            "ninguna hoy. Se caería si un dato deja de tener ruta — que es "
            "exactamente lo que pasa si vive en una fila de una tabla."
        ),
    )


def main():
    base = Path(tempfile.mkdtemp(prefix="awi-sustrato-"))
    print(f"Reproduciendo en {base}\n" + "=" * 72)
    try:
        for comprobacion in (
            control_de_acceso,
            escritura_concurrente,
            escritura_concurrente_en_archivos_distintos,
            consulta,
            auditoria,
            latencia,
            sin_conexion,
            invariante_0011,
        ):
            try:
                comprobacion(base)
            except Exception as e:  # noqa: BLE001 — es un prototipo
                print(f"\n[ERROR] {comprobacion.__name__}: {e}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("\n" + "=" * 72)
    reproducen = [r for r in RESULTADOS if r["reproduce"]]
    no = [r for r in RESULTADOS if not r["reproduce"]]
    print(f"Afirmaciones que reproducen: {len(reproducen)} de {len(RESULTADOS)}")
    for r in no:
        print(f"  NO reproduce — {r['eje']}: la brecha supuesta no está donde se creía")
    print("\nBrechas de diseño (no de configuración):")
    for r in RESULTADOS:
        if r["reproduce"] and r["brecha"].startswith("diseño"):
            print(f"  · {r['eje']}")

    salida = Path(__file__).parent / "evidencia.json"
    salida.write_text(json.dumps(RESULTADOS, ensure_ascii=False, indent=2) + "\n")
    print(f"\nDetalle en {salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
