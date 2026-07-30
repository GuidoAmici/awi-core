"""Purga del historial, con la verificación como razón de ser.

Envuelve `git-filter-repo`. Lo que aporta sobre invocarlo a mano son tres cosas:

1. **Las rutas salen del inventario**, no de una lista escrita a mano. Purgar a
   ciegas y verificar a ojo es cómo se da por cerrado un trabajo a medias.
2. **Vuelve a correr la auditoría después**, con el mismo motor y las mismas
   reglas que la motivaron, y falla si queda algo. Una purga que no se verifica
   con el criterio que la motivó no es una purga, es una esperanza.
3. **Trabaja sobre un espejo**, nunca sobre el repo del operador. El repo
   original queda intacto hasta que el operador decida empujar el resultado —
   el mismo criterio de rescatar en vez de destruir que ya tiene /awi-update.

Distingue dos clases de hallazgo, porque no merecen la misma respuesta:

  - **por ruta** — el archivo entero es el problema (`.claude/tmp/…`). Se purga
    completo y no hay nada que perder.
  - **por contenido** — un archivo por lo demás legítimo tiene una línea
    sensible. Purgar la ruta entera se lleva puesto lo legítimo, así que estas
    quedan afuera salvo pedido explícito.

Uso:
    python3 .claude/skills/shared/scripts/history_purge.py            # sólo mira
    python3 .claude/skills/shared/scripts/history_purge.py --ejecutar

Ver PRD 1 (issue #80), subissue #87.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import history_audit as ha
import sensitive_scan as ss


class PurgaFallida(RuntimeError):
    """La verificación posterior no dio limpio. Ruidoso a propósito."""


@dataclass
class Plan:
    """Lo que la purga haría, derivado del inventario."""

    por_ruta: list[str] = field(default_factory=list)
    por_contenido: list[str] = field(default_factory=list)

    def rutas(self, incluir_contenido: bool = False) -> list[str]:
        return sorted(self.por_ruta + (self.por_contenido if incluir_contenido else []))


@dataclass
class Resultado:
    espejo: Path
    purgadas: list[str]
    antes: ss.Reporte
    despues: ss.Reporte
    residuo: list[ss.Hallazgo]


def planificar(reporte: ss.Reporte) -> Plan:
    """Separa las rutas que se pueden purgar enteras de las que exigen decisión."""
    por_ruta, por_contenido = set(), set()
    for h in reporte.hallazgos:
        if not h.bloquea:
            continue  # ruido-operativo no justifica reescribir historial
        (por_ruta if h.linea is None else por_contenido).add(h.ruta)
    return Plan(
        por_ruta=sorted(por_ruta),
        # Una ruta con hallazgos de las dos clases ya se purga entera.
        por_contenido=sorted(por_contenido - por_ruta),
    )


def _correr(cmd: list[str], cwd: Path) -> str:
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        raise PurgaFallida(f"{' '.join(cmd[:3])}… falló:\n{r.stderr.strip()}")
    return r.stdout


def filter_repo_disponible() -> str | None:
    return shutil.which("git-filter-repo")


def espejar(origen: Path, destino: Path) -> Path:
    """Clon espejo del repo, con todas sus refs.

    `--mirror` y no un clon común: la purga tiene que alcanzar cada rama y cada
    tag, porque una rama abandonada sigue publicando lo que tiene.
    """
    if destino.exists():
        raise PurgaFallida(f"{destino} ya existe; elegí un destino nuevo o borralo")
    destino.parent.mkdir(parents=True, exist_ok=True)
    _correr(["git", "clone", "--mirror", "--no-local", str(origen), str(destino)], destino.parent)
    return destino


def verificar(espejo: Path, reglas: list[ss.Regla], purgadas: list[str]) -> list[ss.Hallazgo]:
    """Residuo: hallazgos que sobreviven en las rutas que se purgaron.

    Restringido a las rutas purgadas a propósito. Si el operador dejó afuera un
    hallazgo por contenido, la auditoría lo sigue reportando y está bien: no es
    residuo de esta purga.
    """
    reporte = ha.auditar(espejo, reglas)
    purgadas_set = set(purgadas)
    return [h for h in reporte.hallazgos if h.ruta in purgadas_set]


def purgar(
    origen: Path,
    destino: Path,
    reglas: list[ss.Regla],
    incluir_contenido: bool = False,
) -> Resultado:
    """Espeja, reescribe, y verifica. Falla si queda residuo."""
    if not filter_repo_disponible():
        raise PurgaFallida(
            "git-filter-repo no está instalado. `pipx install git-filter-repo` "
            "o el paquete de la distribución."
        )

    antes = ha.auditar(origen, reglas)
    plan = planificar(antes)
    rutas = plan.rutas(incluir_contenido)
    if not rutas:
        raise PurgaFallida("el inventario no señala ninguna ruta a purgar")

    espejo = espejar(origen, destino)

    argumentos = ["git-filter-repo", "--invert-paths", "--force"]
    for ruta in rutas:
        argumentos += ["--path", ruta]
    _correr(argumentos, espejo)
    _correr(["git", "reflog", "expire", "--expire=now", "--all"], espejo)
    _correr(["git", "gc", "--prune=now", "--aggressive", "--quiet"], espejo)

    residuo = verificar(espejo, reglas, rutas)
    despues = ha.auditar(espejo, reglas)

    resultado = Resultado(
        espejo=espejo, purgadas=rutas, antes=antes, despues=despues, residuo=residuo
    )
    if residuo:
        raise PurgaFallida(
            f"la purga dejó {len(residuo)} hallazgo(s) en rutas que decía haber purgado:\n"
            + "\n".join(f"  {h}" for h in residuo[:10])
        )
    return resultado


# ── Reporte ──────────────────────────────────────────────────────────────────

def describir_plan(plan: Plan, antes: ss.Reporte) -> str:
    lineas = [
        f"Inventario: {len(antes.hallazgos)} hallazgo(s), "
        + ", ".join(f"{c}={n}" for c, n in antes.por_categoria().items()),
        "",
        f"Se purgarían {len(plan.por_ruta)} ruta(s) enteras (el archivo es el problema):",
    ]
    lineas += [f"   {r}" for r in plan.por_ruta[:40]]
    if len(plan.por_ruta) > 40:
        lineas.append(f"   … y {len(plan.por_ruta) - 40} más")

    if plan.por_contenido:
        lineas += [
            "",
            f"Quedan afuera {len(plan.por_contenido)} ruta(s) con hallazgos por contenido.",
            "Son archivos por lo demás legítimos: purgar la ruta entera se lleva puesto",
            "lo legítimo. Requieren decisión explícita (--incluir-contenido):",
        ]
        lineas += [f"   {r}" for r in plan.por_contenido]
    return "\n".join(lineas)


def describir_resultado(r: Resultado) -> str:
    return "\n".join(
        [
            f"✓ Purga verificada en el espejo: {r.espejo}",
            f"  Rutas purgadas: {len(r.purgadas)}",
            f"  Hallazgos antes:  {len(r.antes.hallazgos)}",
            f"  Hallazgos después: {len(r.despues.hallazgos)}",
            f"  Residuo en las rutas purgadas: {len(r.residuo)}",
            "",
            "El repo original NO se tocó. Para publicar el resultado, desde el espejo:",
            f"  git -C {r.espejo} remote add origin <url>",
            f"  git -C {r.espejo} push --force --mirror origin",
            "",
            "Y en cada instancia, /awi-update trae el historial nuevo.",
            "",
            ha.LIMITE,
        ]
    )


def main(argv: list[str] | None = None) -> int:
    from paths import AWI_ROOT

    p = argparse.ArgumentParser(description="Purga del historial con verificación posterior.")
    p.add_argument("--repo", default=".", type=Path)
    p.add_argument("--reglas", type=Path, default=AWI_ROOT / ss.REGLAS_SENSIBLES)
    p.add_argument("--destino", type=Path, default=None, help="dónde crear el espejo purgado")
    p.add_argument("--ejecutar", action="store_true", help="sin esto, sólo describe el plan")
    p.add_argument(
        "--incluir-contenido",
        action="store_true",
        help="purgar también las rutas señaladas sólo por contenido (se van enteras)",
    )
    args = p.parse_args(argv)

    try:
        reglas = ss.cargar_reglas(args.reglas)
        if not args.ejecutar:
            antes = ha.auditar(args.repo, reglas)
            print(describir_plan(planificar(antes), antes))
            print("\n(sin --ejecutar: no se creó ni se modificó nada)")
            if not filter_repo_disponible():
                print("\n⚠ git-filter-repo no está instalado: --ejecutar fallaría.")
            return 0

        destino = args.destino or args.repo.resolve().parent / (
            args.repo.resolve().name + "-purgado.git"
        )
        print(describir_resultado(purgar(args.repo, destino, reglas, args.incluir_contenido)))
        return 0
    except (ss.ReglasInvalidas, ha.ErrorDeGit, PurgaFallida) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
