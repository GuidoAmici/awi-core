#!/usr/bin/env python3
"""Traer la última versión del harness a esta instancia.

Las instancias consumidoras siguen `main`, que sólo avanza por fast-forward
desde un commit de `dev` que pasó los tests (ADR 0015). Actualizar es entonces
un reset duro a `origin/main`: los compañeros son consumidores del harness, no
coautores (ADR 0014), así que no hay merge y por lo tanto no hay conflicto que
mostrarle a alguien que no usa git.

`_data/` está en .gitignore, así que el reset nunca toca datos privados: perfiles
de usuario, workspaces de org y los repos clonados adentro quedan intactos.

La rama decide el ref *y* la operación. En `main` es reset duro. En cualquier
otra rama es `merge --ff-only`, que no puede destruir nada: si divergió o el
árbol está sucio, falla y lo explica. Cambiar sólo el ref y seguir reseteando
rompería el trabajo del mantenedor igual — el ref no hace daño, la operación sí.

**Nada se destruye, ni siquiera en el reset.** Antes de tocar el árbol, todo
trabajo local se rescata: lo no commiteado a un stash con nombre, los commits
locales a una rama `respaldo/`. El reset produce el resultado correcto —el
harness idéntico a lo publicado, sin conflictos— pero no hace falta pagarlo con
trabajo perdido. Importa sobre todo en máquinas que estuvieron meses sin
actualizarse, donde es probable que haya algo local que nadie recuerda.

Uso:
    python3 awi_update.py            # reporta y actualiza
    python3 awi_update.py --check    # sólo reporta, no toca nada

Códigos de salida:
    0  actualizado, o ya al día
    1  no se pudo — remoto inalcanzable, rama divergida o árbol sucio
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared" / "scripts"))
from paths import AWI_ROOT

DISTRIBUTION_BRANCH = "main"
WORK_BRANCH = "dev"

TYPE_LABELS = {
    "feat": "Nuevo",
    "fix": "Arreglado",
    "refactor": "Reescrito",
    "perf": "Rendimiento",
    "docs": "Documentación",
    "ci": "CI",
    "chore": "Mantenimiento",
    "test": "Tests",
}
CONVENTIONAL = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]*)\))?!?:\s*(?P<subject>.+)$")


def git(*args: str, check: bool = False) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *args], cwd=AWI_ROOT, capture_output=True, text=True)
    if check and r.returncode != 0:
        die(f"git {' '.join(args)} falló:\n{r.stderr.strip()}")
    return r


def out(*args: str) -> str:
    return git(*args).stdout.strip()


def die(msg: str, code: int = 1) -> None:
    sys.stdout.flush()  # sin esto el error aparece antes del reporte que lo explica
    print(f"✗ {msg}", file=sys.stderr)
    sys.exit(code)


def quiet_stderr(text: str) -> str:
    """Descartar las líneas `hint:` de git.

    Le dicen al operador que corra `git rebase` o `git merge --no-ff` — es
    exactamente el detalle de git que /awi-update existe para no mostrar.
    """
    return "\n".join(
        f"  {ln.strip()}" for ln in text.splitlines() if ln.strip() and not ln.startswith("hint:")
    )


def current_branch() -> str:
    return out("rev-parse", "--abbrev-ref", "HEAD")


def version_at(ref: str) -> str:
    """Leer version.txt en un ref. Devuelve '?' si no existe todavía."""
    r = git("show", f"{ref}:version.txt")
    return r.stdout.strip() if r.returncode == 0 else "?"


def local_changes() -> list[str]:
    """Archivos del harness modificados localmente, que el reset va a descartar.

    No pasa por out(): en --porcelain la primera columna es significativa y un
    .strip() sobre el stdout completo se come el espacio inicial de la primera
    línea, corriendo el nombre del archivo un carácter.
    """
    raw = git("status", "--porcelain", "--untracked-files=no").stdout
    return [ln[3:] for ln in raw.splitlines() if ln.strip()]


def incoming(old: str, new: str) -> list[tuple[str, str, str]]:
    """(tipo, scope, asunto) de cada commit que entra, del más nuevo al más viejo."""
    if old == new:
        return []
    subjects = out("log", "--format=%s", f"{old}..{new}").splitlines()
    parsed = []
    for s in subjects:
        m = CONVENTIONAL.match(s)
        if m:
            parsed.append((m["type"], m["scope"] or "", m["subject"]))
        else:
            parsed.append(("", "", s))
    return parsed


def describe(commits: list[tuple[str, str, str]]) -> None:
    """Agrupar por tipo, en el orden de TYPE_LABELS, y listar."""
    grouped: dict[str, list[str]] = {}
    for typ, scope, subject in commits:
        label = TYPE_LABELS.get(typ, "Otros")
        grouped.setdefault(label, []).append(f"{scope + ': ' if scope else ''}{subject}")

    ordered = list(dict.fromkeys(list(TYPE_LABELS.values()) + ["Otros"]))
    for label in ordered:
        if label not in grouped:
            continue
        print(f"\n  {label}")
        for line in grouped[label]:
            print(f"    · {line}")


def rescue(branch: str, target: str, dirty: bool) -> list[str]:
    """Poner a salvo todo trabajo local antes de una operación destructiva.

    El reset produce el resultado correcto —el harness idéntico a lo publicado,
    sin conflictos que mostrar— pero no hace falta pagarlo con trabajo perdido.
    Dos rescates, porque son dos clases distintas de trabajo:

      · no commiteado  → stash con nombre y fecha
      · commits locales → rama respaldo/<rama>-<fecha>

    Devuelve las líneas a reportar. Si algún rescate falla, aborta: perder
    trabajo en silencio es peor que no actualizar.
    """
    stamp = subprocess.run(["date", "+%Y%m%d-%H%M"], capture_output=True, text=True).stdout.strip()
    rescued = []

    ahead = git("rev-list", "--count", f"{target}..HEAD").stdout.strip()
    if ahead.isdigit() and int(ahead) > 0:
        backup = f"respaldo/{branch}-{stamp}"
        if git("branch", backup, "HEAD").returncode != 0:
            die(f"no se pudo respaldar {ahead} commit(s) local(es) en '{backup}'. No se tocó nada.")
        rescued.append(f"{ahead} commit(s) local(es) → rama '{backup}'")

    if dirty:
        r = git("stash", "push", "--include-untracked", "-m", f"awi-update {stamp}")
        if r.returncode != 0:
            die(f"no se pudo guardar los cambios sin commitear. No se tocó nada:\n{quiet_stderr(r.stderr)}")
        rescued.append(f"cambios sin commitear → stash 'awi-update {stamp}' (verlos con: git stash list)")

    return rescued


def promotion_lag() -> int | None:
    """Cuántos commits de `dev` no llegaron a `main` todavía.

    Diagnóstico, no gate: la promoción anterior falló en 4 de 4 corridas durante
    días sin que nadie lo notara (ADR 0015). Si se vuelve a colgar, tiene que
    verse desde acá aunque el CI esté callado.
    """
    r = git("rev-list", "--count", f"origin/{DISTRIBUTION_BRANCH}..origin/{WORK_BRANCH}")
    return int(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip().isdigit() else None


def main() -> None:
    ap = argparse.ArgumentParser(description="Actualizar el harness de AWI")
    ap.add_argument("--check", action="store_true", help="Sólo reportar, sin tocar nada")
    args = ap.parse_args()

    if not (AWI_ROOT / ".git").exists():
        die(f"{AWI_ROOT} no es un repo git.")

    branch = current_branch()
    consuming = branch == DISTRIBUTION_BRANCH

    print("Buscando actualizaciones…")
    if git("fetch", "origin", "--tags", "--quiet").returncode != 0:
        die("no se pudo contactar el remoto. ¿Hay conexión?")

    # La rama decide el ref *y* la operación. Reset duro sólo en la rama de
    # distribución, donde no hay trabajo local legítimo. En cualquier otra,
    # fast-forward: no puede destruir nada, y si divergió falla y lo dice.
    # Cambiar sólo el ref y seguir reseteando rompería el trabajo del
    # mantenedor igual — el ref no es lo que hace daño, la operación sí.
    target = f"origin/{DISTRIBUTION_BRANCH}" if consuming else f"origin/{branch}"
    if git("rev-parse", "--verify", "--quiet", target).returncode != 0:
        die(
            f"el remoto no tiene '{target}'."
            + ("" if consuming else f" La rama '{branch}' es local: no hay nada que traer.")
        )

    before, after = out("rev-parse", "HEAD"), out("rev-parse", target)
    v_before, v_after = version_at("HEAD"), version_at(target)
    commits = incoming(before, after)
    dirty = local_changes()
    lag = promotion_lag()

    if not consuming:
        print(f"  Estás en '{branch}', no en '{DISTRIBUTION_BRANCH}': fast-forward, sin reset.")

    if not commits:
        print(f"✓ Ya estás al día — versión {v_before}.")
    else:
        version_note = f"{v_before} → {v_after}" if v_before != v_after else f"{v_after} (sin cambio de versión)"
        print(f"\n{len(commits)} cambio(s) para traer — {version_note}:")
        describe(commits)

    if dirty:
        if consuming:
            print(f"\n  {len(dirty)} archivo(s) del harness modificados localmente, se guardan en un stash:")
        else:
            print(f"\n  ⚠ {len(dirty)} archivo(s) con cambios sin commitear:")
        for f in dirty[:10]:
            print(f"    · {f}")
        if len(dirty) > 10:
            print(f"    · … y {len(dirty) - 10} más")
        print(
            "    El harness lo mantiene awi-core; si necesitás un cambio, pedilo."
            if consuming
            else "    Commiteálos o guardálos antes: el fast-forward no corre con el árbol sucio."
        )

    if lag:
        print(
            f"\n  ⚠ Diagnóstico: '{WORK_BRANCH}' tiene {lag} commit(s) que no llegaron a "
            f"'{DISTRIBUTION_BRANCH}'.\n"
            f"    O están esperando que pasen los tests, o la promoción se colgó."
        )

    if args.check:
        print("\n(--check: no se modificó nada.)")
        return

    if not commits and not (dirty and consuming):
        return

    if consuming:
        for line in rescue(branch, target, bool(dirty)):
            print(f"  ↪ Rescatado: {line}")
        git("reset", "--hard", target, check=True)
    else:
        r = git("merge", "--ff-only", target)
        if r.returncode != 0:
            die(
                f"no se pudo traer '{branch}' sin riesgo. No se tocó nada.\n\n"
                f"{quiet_stderr(r.stderr)}\n\n"
                f"  Tu rama tiene commits que el remoto no tiene, o el árbol está sucio.\n"
                f"  Traerla requeriría decidir qué versión gana, y eso no lo decide\n"
                f"  esta skill. Resolvelo y volvé a correr."
            )

    print(f"\n✓ Harness actualizado a {version_at('HEAD')} ({out('rev-parse', '--short', 'HEAD')}).")
    print("  Tus datos en _data/ no se tocaron.")

    install_git_hooks()


def install_git_hooks() -> None:
    """Apuntar core.hooksPath a los hooks versionados de AWI.

    Va acá porque `core.hooksPath` es config local: los hooks viajan con el
    harness, pero la config que los activa no viaja con un clone. /awi-update ya
    es el camino por el que el harness llega a una instancia, así que es el lugar
    donde la prevención de material sensible se enciende sin que el operador
    tenga que saber que existe. Ver PRD 1 (issue #80).

    Nunca corta la actualización: el harness ya quedó actualizado.
    """
    try:
        import staged_scan

        estado = staged_scan.instalar(AWI_ROOT)
    except Exception as e:  # noqa: BLE001 — el update ya terminó bien
        print(f"  ⚠ No se pudieron activar los hooks de git: {e}")
        return
    if "ya instalado" not in estado:
        print(f"  ✓ Hooks de git activados — {estado}")


if __name__ == "__main__":
    main()
