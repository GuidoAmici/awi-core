#!/usr/bin/env python3
"""Mecánica del ciclo de contexto compartido: traer, mirar, publicar.

Reemplaza a `/awi-sync`, que nació para reapuntar submódulos —cosa que ya no
existe— y cuyo resto de comportamiento era peligroso con varios operadores:
hacía `git add -A` y commiteaba todo con el mensaje fijo
`"chore(sync): stage local changes"`, y ante un rebase fallido marcaba `failed`,
retornaba y seguía con el próximo repo **sin abortar el rebase** — dejando el
repo a mitad de una operación que hay que sacar con comandos de git.

Este script es sólo la mecánica. El juicio —cuándo traer, cuándo sugerir
publicar, cómo se llama cada commit, si hay que preguntar— vive en
INSTRUCTIONS.md. La razón es empírica: `log_command` se invoca por instrucción en
22 archivos SKILL.md y el registro subcuenta, así que sabemos que las
instrucciones se cumplen a veces. Para un log alcanza; para traer el contexto de
otro operador, no. Ver ADR 0014 y 0015.

Alcance: los repos de **contexto** — orgs, sus codebases y el repo del propio
operador. Los repos marcados `upstream` quedan afuera: son dependencias, no
contexto, y su política es otra (ADR 0012).

Uso:
    python3 context_sync.py pull
    python3 context_sync.py status
    python3 context_sync.py push --repo <nombre> --message "<mensaje>"

Códigos de salida:
    0  todo bien
    1  error de configuración o de git
    3  se completó, pero algún repo necesita atención humana
"""

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sensitive_scan as ss
from manifest import Repo, plan
from paths import AWI_ROOT

NEEDS_ATTENTION = 3


@dataclass
class Result:
    repo: str
    state: str          # pulled · al-día · conflicto · sensible · sin-clonar · error
    detail: str = ""
    dirty: int = 0
    ahead: int = 0
    #: Rutas con material sensible, cuando `state == "sensible"`.
    hallazgos: tuple[str, ...] = ()


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)


def context_repos(con_codebases: bool = False) -> list[Repo]:
    """Repos que el ciclo automático toca: agendas de org y el repo del operador.

    Un repo `upstream` es una dependencia —comportamiento que se ejecuta— y no
    contexto —datos sobre los que se trabaja. Mezclarlos fue el error que el
    ADR 0012 corrige.

    **Los codebases quedan afuera por defecto.** Su contenido no es contexto que
    se pasa entre operadores: es código, y avanza en una sesión de desarrollo con
    un desarrollador mirando. Traerlos automáticamente es además destructivo — un
    `pull --rebase origin stg` con una rama de feature checkeada reescribe la rama
    del desarrollador sin que nadie lo pida. Ver ADR 0020.
    """
    repos, warnings = plan(AWI_ROOT)
    for w in warnings:
        print(f"  ⚠ {w}", file=sys.stderr)
    return [r for r in repos if not r.upstream and (con_codebases or not r.is_codebase)]


def dirty_count(path: Path) -> int:
    raw = git(path, "status", "--porcelain").stdout
    return len([ln for ln in raw.splitlines() if ln.strip()])


def ahead_count(path: Path, branch: str) -> int:
    r = git(path, "rev-list", "--count", f"origin/{branch}..HEAD")
    return int(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip().isdigit() else 0


def current_branch(path: Path) -> str:
    return git(path, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()


def pull_one(r: Repo) -> Result:
    """Traer un repo sin dejarlo nunca a mitad de un rebase.

    `--autostash` deja trabajar con el árbol sucio, que es el estado normal al
    abrir una sesión. Si el rebase falla, se aborta y el repo vuelve a como
    estaba: preferimos reportar que un repo necesita atención antes que dejarlo
    en un estado del que hay que salir con comandos de git.
    """
    if not (r.path / ".git").exists():
        return Result(r.name, "sin-clonar", "corré /awi-initialize")

    # Rebasear la rama activa sobre otra reescribe el trabajo de quien la abrió.
    # El guard va antes del fetch: no hay nada que traer a un repo que no vamos a
    # tocar.
    activa = current_branch(r.path)
    if activa != r.branch:
        return Result(
            r.name, "otra-rama",
            f"estás en «{activa}»; traer «{r.branch}» acá reescribiría tu rama",
            dirty=dirty_count(r.path),
        )

    if git(r.path, "fetch", "origin", "--quiet").returncode != 0:
        return Result(r.name, "error", "no se pudo contactar el remoto")

    before = git(r.path, "rev-parse", "HEAD").stdout.strip()
    res = git(r.path, "pull", "--rebase", "--autostash", "origin", r.branch)

    if res.returncode != 0:
        git(r.path, "rebase", "--abort")
        return Result(
            r.name, "conflicto",
            "tus cambios y los de otra persona tocan lo mismo; el repo quedó como estaba",
            dirty=dirty_count(r.path), ahead=ahead_count(r.path, r.branch),
        )

    after = git(r.path, "rev-parse", "HEAD").stdout.strip()
    state = "pulled" if before != after else "al-día"
    return Result(r.name, state, dirty=dirty_count(r.path), ahead=ahead_count(r.path, r.branch))


def pending_paths(path: Path) -> list[str]:
    """Rutas que un `git add -A` levantaría. El renombre entra por su destino."""
    rutas = []
    for ln in git(path, "status", "--porcelain").stdout.splitlines():
        if not ln.strip():
            continue
        ruta = ln[3:]
        if " -> " in ruta:          # R  viejo -> nuevo
            ruta = ruta.split(" -> ", 1)[1]
        rutas.append(ruta.strip('"'))
    return rutas


def scan_sensitive(path: Path) -> ss.Reporte:
    """Escanear lo que está por publicarse, leyendo del árbol de trabajo.

    El motor de `sensitive_scan` no sabe de git a propósito, y acá se aprovecha:
    escanear antes de `git add -A` deja el índice intacto cuando hay hallazgos,
    en vez de tener que revertir un staging que quizás el operador armó a mano.

    Este escaneo no reemplaza al hook de pre-commit — lo cubre donde el hook no
    llega. `core.hooksPath` apunta a un directorio del harness, así que los repos
    de contexto, que viven en `_data/` y son repos aparte, nunca lo tuvieron. Sin
    esto, publicar automáticamente sería `git add -A` sin ninguna red debajo.
    """
    reglas = ss.cargar_reglas(AWI_ROOT / ss.REGLAS_SENSIBLES)
    entradas = []
    for ruta in pending_paths(path):
        archivo = path / ruta
        try:
            crudo = archivo.read_bytes()
            contenido = None if len(crudo) > ss.MAX_BYTES else crudo.decode("utf-8", errors="replace")
        except OSError:             # borrado, o ilegible: se evalúa por la ruta
            contenido = None
        entradas.append(ss.Entrada(ruta, contenido))
    return ss.escanear(entradas, reglas)


def push_one(r: Repo, message: str) -> Result:
    """Commitear lo que haya y publicarlo, con el mensaje que decidió la IA.

    El mensaje llega por parámetro a propósito. `/awi-sync` usaba una constante,
    y el resultado fue un historial compartido que es una pared de líneas
    idénticas — inútil para saber qué cambió y para generar un changelog.
    """
    if not (r.path / ".git").exists():
        return Result(r.name, "sin-clonar")

    # El commit va a la rama activa, pero el push publica la del manifiesto. Si no
    # son la misma, publicar «con éxito» dejaría el trabajo del operador en una rama
    # local mientras se sube otra cosa — el peor resultado posible para alguien que
    # por diseño no mira git. Un codebase con una rama de feature checkeada es el
    # caso normal, no el raro.
    activa = current_branch(r.path)
    if activa != r.branch:
        return Result(
            r.name, "otra-rama",
            f"estás en «{activa}» y el ciclo publica «{r.branch}»; nadie decide eso por vos",
            dirty=dirty_count(r.path),
        )

    if dirty_count(r.path):
        try:
            reporte = scan_sensitive(r.path)
        except (ss.ReglasInvalidas, OSError) as e:
            return Result(r.name, "error", f"no se pudo escanear material sensible: {e}")

        if reporte.bloqueantes:
            return Result(
                r.name, "sensible",
                "hay material sensible entre los cambios; no se publicó nada",
                dirty=dirty_count(r.path),
                hallazgos=tuple(str(h) for h in reporte.bloqueantes),
            )

        git(r.path, "add", "-A")
        res = git(r.path, "commit", "-m", message)
        if res.returncode != 0 and "nothing to commit" not in (res.stdout + res.stderr):
            return Result(r.name, "error", f"commit falló: {res.stderr.strip()}")

    if ahead_count(r.path, r.branch) == 0:
        return Result(r.name, "al-día", "nada para publicar")

    res = git(r.path, "push", "origin", r.branch)
    if res.returncode != 0:
        return Result(
            r.name, "conflicto",
            "el remoto tiene cambios que no tenés; traé primero (pull) y volvé a intentar",
        )
    return Result(r.name, "publicado")


def report(results: list[Result], header: str) -> int:
    icons = {"pulled": "↓", "publicado": "↑", "al-día": "·", "conflicto": "⚠",
             "sensible": "⛔", "otra-rama": "⌥", "sin-clonar": "○", "error": "✗"}
    needs_human = ("conflicto", "sensible", "otra-rama", "error")
    print(f"\n{header}")
    attention = []
    for res in sorted(results, key=lambda x: (x.state not in needs_human, x.repo)):
        line = f"  {icons.get(res.state, '?')} {res.repo:28} {res.state}"
        if res.dirty:
            line += f"  ({res.dirty} sin commitear)"
        print(line)
        if res.detail:
            print(f"      {res.detail}")
        for h in res.hallazgos:
            print(f"      {h}")
        if res.state in needs_human:
            attention.append(res.repo)

    if attention:
        print(f"\n  {len(attention)} repo(s) necesitan atención: {', '.join(attention)}")
        print("  Ningún repo quedó a medias — todos están en un estado del que se puede seguir.")
        return NEEDS_ATTENTION
    return 0


def report_codebases() -> None:
    """Qué hay pendiente en los codebases, sin tocar ninguno.

    Se informa y no se opera: enterarse de que hay trabajo sin publicar es útil;
    publicarlo automáticamente es lo que la sesión de desarrollo hace con un
    desarrollador mirando.
    """
    pendientes = []
    for r in context_repos(con_codebases=True):
        if not r.is_codebase or not (r.path / ".git").exists():
            continue
        activa, dirty = current_branch(r.path), dirty_count(r.path)
        ahead = ahead_count(r.path, r.branch) if activa == r.branch else 0
        bits = []
        if dirty:
            bits.append(f"{dirty} archivo(s) sin commitear")
        if ahead:
            bits.append(f"{ahead} commit(s) sin subir")
        if activa != r.branch:
            bits.append(f"en «{activa}», no en «{r.branch}»")
        if bits:
            pendientes.append(f"  · {r.name:28} {', '.join(bits)}")

    if pendientes:
        print("\nCodebases — fuera del ciclo, se ven pero no se tocan:")
        print("\n".join(pendientes))
        print("  El código avanza en su propia sesión, con el desarrollador mirando.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Ciclo de contexto compartido")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for nombre, ayuda in (("pull", "Traer los cambios de los repos de contexto"),
                          ("status", "Qué hay sin commitear y sin publicar, por repo")):
        s = sub.add_parser(nombre, help=ayuda)
        s.add_argument("--con-codebases", action="store_true",
                       help="incluir los codebases: sólo para una sesión de desarrollo supervisada")
    p = sub.add_parser("push", help="Commitear y publicar un repo")
    p.add_argument("--repo", required=True, help="Nombre del repo, como aparece en pull/status")
    p.add_argument("--message", required=True, help="Mensaje de commit (Conventional Commits)")
    p.add_argument("--con-codebases", action="store_true",
                   help="permitir publicar un codebase: sólo para una sesión de desarrollo supervisada")
    args = ap.parse_args()

    repos = context_repos(con_codebases=args.con_codebases)
    if not repos:
        print("No hay repos de contexto materializados.")
        return

    if args.cmd == "pull":
        sys.exit(report([pull_one(r) for r in repos], "Contexto compartido — traído:"))

    if args.cmd == "status":
        results = []
        for r in repos:
            if not (r.path / ".git").exists():
                results.append(Result(r.name, "sin-clonar"))
                continue
            activa = current_branch(r.path)
            results.append(Result(
                r.name, "al-día" if activa == r.branch else "otra-rama",
                "" if activa == r.branch else f"en «{activa}», el ciclo publica «{r.branch}»",
                dirty=dirty_count(r.path), ahead=ahead_count(r.path, r.branch),
            ))
        pending = [x for x in results if x.dirty or x.ahead or x.state == "otra-rama"]
        if not pending:
            print("Todo publicado — no hay nada sin commitear ni sin subir.")
        else:
            print("\nSin publicar:")
            for x in pending:
                bits = []
                if x.dirty:
                    bits.append(f"{x.dirty} archivo(s) sin commitear")
                if x.ahead:
                    bits.append(f"{x.ahead} commit(s) sin subir")
                print(f"  · {x.repo:28} {', '.join(bits) or 'nada pendiente'}")
                if x.detail:
                    print(f"      ⌥ {x.detail}")
        if not args.con_codebases:
            report_codebases()
        return

    match = [r for r in repos if r.name == args.repo]
    if not match:
        conocidos = {r.name: r for r in context_repos(con_codebases=True)}
        if args.repo in conocidos and conocidos[args.repo].is_codebase:
            print(f"✗ '{args.repo}' es un codebase: el ciclo automático no publica código.\n"
                  f"  El código avanza en su propia sesión, con el desarrollador mirando.\n"
                  f"  Si esta es esa sesión, agregá --con-codebases.", file=sys.stderr)
        else:
            print(f"✗ '{args.repo}' no es un repo de contexto. Opciones: {', '.join(r.name for r in repos)}",
                  file=sys.stderr)
        sys.exit(1)
    sys.exit(report([push_one(match[0], args.message)], f"Publicando {args.repo}:"))


if __name__ == "__main__":
    main()
