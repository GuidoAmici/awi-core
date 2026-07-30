#!/usr/bin/env python3
"""Traer la última versión del harness a esta instancia.

Las instancias consumidoras siguen `main`, que sólo avanza por fast-forward
desde un commit de `dev` que pasó los tests (ADR 0015). Actualizar es entonces
un reset duro a `origin/main`: los compañeros son consumidores del harness, no
coautores (ADR 0014), así que no hay merge y por lo tanto no hay conflicto que
mostrarle a alguien que no usa git.

`_data/` está en .gitignore, así que el reset nunca toca datos privados: perfiles
de usuario, workspaces de org y los repos clonados adentro quedan intactos.

Uso:
    python3 awi_update.py            # reporta y actualiza
    python3 awi_update.py --check    # sólo reporta, no toca nada

Códigos de salida:
    0  actualizado, o ya al día
    1  error de git o de red
    2  rechazado — esta instancia es de desarrollo del harness
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
    print(f"✗ {msg}", file=sys.stderr)
    sys.exit(code)


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
    if branch == WORK_BRANCH:
        die(
            f"esta instancia está en '{WORK_BRANCH}', la rama de desarrollo del harness.\n"
            f"  /awi-update es para instancias consumidoras, que siguen '{DISTRIBUTION_BRANCH}'.\n"
            f"  Un reset duro acá borraría trabajo del harness sin pushear.",
            code=2,
        )

    print("Buscando actualizaciones…")
    if git("fetch", "origin", "--tags", "--quiet").returncode != 0:
        die("no se pudo contactar el remoto. ¿Hay conexión?")

    target = f"origin/{DISTRIBUTION_BRANCH}"
    if git("rev-parse", "--verify", "--quiet", target).returncode != 0:
        die(f"el remoto no tiene la rama '{DISTRIBUTION_BRANCH}'.")

    before, after = out("rev-parse", "HEAD"), out("rev-parse", target)
    v_before, v_after = version_at("HEAD"), version_at(target)
    commits = incoming(before, after)
    dirty = local_changes()
    lag = promotion_lag()

    if not commits and branch == DISTRIBUTION_BRANCH:
        print(f"✓ Ya estás al día — versión {v_before}.")
    else:
        if branch != DISTRIBUTION_BRANCH:
            print(f"  Esta instancia está en '{branch}'; se cambia a '{DISTRIBUTION_BRANCH}'.")
        if commits:
            version_note = f"{v_before} → {v_after}" if v_before != v_after else f"{v_after} (sin cambio de versión)"
            print(f"\n{len(commits)} cambio(s) para traer — {version_note}:")
            describe(commits)
        if dirty:
            print(f"\n  ⚠ {len(dirty)} archivo(s) del harness modificados localmente se van a descartar:")
            for f in dirty[:10]:
                print(f"    · {f}")
            if len(dirty) > 10:
                print(f"    · … y {len(dirty) - 10} más")
            print("    El harness lo mantiene awi-core; si necesitás un cambio, pedilo.")

    if lag:
        print(
            f"\n  ⚠ Diagnóstico: '{WORK_BRANCH}' tiene {lag} commit(s) que no llegaron a "
            f"'{DISTRIBUTION_BRANCH}'.\n"
            f"    O están esperando que pasen los tests, o la promoción se colgó."
        )

    if args.check:
        print("\n(--check: no se modificó nada.)")
        return

    if not commits and branch == DISTRIBUTION_BRANCH and not dirty:
        return

    if branch != DISTRIBUTION_BRANCH:
        git("checkout", DISTRIBUTION_BRANCH, check=True)
    git("reset", "--hard", target, check=True)
    print(f"\n✓ Harness actualizado a {version_at('HEAD')} ({out('rev-parse', '--short', 'HEAD')}).")
    print("  Tus datos en _data/ no se tocaron.")


if __name__ == "__main__":
    main()
