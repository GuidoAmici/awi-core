"""trace_id y cadena de fallback: qué hizo un delegado, y qué pasa si no pudo.

**El trace_id** es la señal que no existía. Cuando un delegado hacía algo, no
había forma de correlacionar el issue que lo originó con los commits que produjo:
`status.json` no lo sabía, el log se llamaba por el slug, e `inbox.md` traía una
línea sin identificador. «Qué commits salieron de este issue» era una pregunta sin
respuesta.

Deriva del issue de origen a propósito, así que es legible y reconstruible: mirando
`awi-42-a3f1c8` se sabe que salió del issue 42, y buscando ese texto en el log de
git aparecen sus commits.

**La cadena de fallback** existe porque hoy un `exit != 0` produce una línea en
`inbox.md` y nada más — sin reintento, sin degradado, sin escalamiento. El
principio es que el sistema **siempre produce algo**: una respuesta degradada
estructurada es mejor que un fallo mudo, porque un fallo mudo se descubre tres
días después.

Módulo puro salvo `escalar()`, que escribe. Ver PRD 2 (issue #81), subissues #93
y #94.
"""

from __future__ import annotations

import json
import os
import re
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

PREFIJO = "awi"

#: Sufijo aleatorio: dos delegados sobre el mismo issue tienen que distinguirse.
SUFIJO_BYTES = 3

TRACE_RE = re.compile(rf"\b{PREFIJO}-(\d+)-([0-9a-f]{{{SUFIJO_BYTES * 2}}})\b")

#: Variable de entorno con la que el delegado recibe su trace_id, para poder
#: ponerlo en los mensajes de commit que produce.
ENV_TRACE = "AWI_TRACE_ID"


# ── Generación y parsing ─────────────────────────────────────────────────────

def nuevo(issue: int | str, sufijo: str | None = None) -> str:
    """`awi-42-a3f1c8`. Derivado del issue, así que es reconstruible a la vista."""
    numero = str(issue).lstrip("#")
    if not numero.isdigit():
        raise ValueError(f"el issue de origen tiene que ser un número, no «{issue}»")
    return f"{PREFIJO}-{numero}-{sufijo or secrets.token_hex(SUFIJO_BYTES)}"


def issue_de(trace_id: str) -> int:
    """El issue del que salió un trace_id."""
    m = TRACE_RE.fullmatch(trace_id.strip())
    if not m:
        raise ValueError(f"«{trace_id}» no tiene la forma de un trace_id")
    return int(m.group(1))


def extraer(texto: str) -> list[str]:
    """Los trace_id que aparecen en un texto — un log de git, un informe, un log."""
    return [f"{PREFIJO}-{n}-{s}" for n, s in TRACE_RE.findall(texto)]


def entorno(trace_id: str) -> dict[str, str]:
    """El entorno con el que arranca el delegado, para que propague su trace_id."""
    return {ENV_TRACE: trace_id}


def instruccion_de_commit(trace_id: str) -> str:
    """Lo que se le pide al delegado sobre sus commits.

    El trailer va en el mensaje y no en el asunto: `git log --grep` lo encuentra
    igual, y el asunto sigue siendo legible y válido como Conventional Commit.
    """
    return (
        f"En cada commit que hagas, agregá este trailer al final del mensaje:\n"
        f"    AWI-Trace: {trace_id}\n"
        f"Es lo que permite reconstruir después qué commits salieron de este "
        f"issue. Sin él, ese vínculo no existe en ninguna parte."
    )


TRAILER_RE = re.compile(rf"^AWI-Trace:\s*({PREFIJO}-\d+-[0-9a-f]+)\s*$", re.MULTILINE)


def commits_de(log_de_git: str, trace_id: str) -> list[str]:
    """Los SHA cuyo mensaje lleva el trailer de este trace_id.

    Espera la salida de `git log --format=%H%n%B%n<separador>`.
    """
    encontrados = []
    for bloque in log_de_git.split("\x00"):
        lineas = bloque.strip().splitlines()
        if not lineas:
            continue
        sha = lineas[0].strip()
        if not re.fullmatch(r"[0-9a-f]{7,40}", sha):
            continue
        for m in TRAILER_RE.finditer("\n".join(lineas[1:])):
            if m.group(1) == trace_id:
                encontrados.append(sha)
                break
    return encontrados


# ── Cadena de fallback ───────────────────────────────────────────────────────

#: Estados finales que ameritan reintentar. La distinción no es cosmética: un
#: timeout o una muerte por señal puede ser transitorio; un `exit 1` del agente
#: significa que corrió y decidió que no podía, y reintentarlo idéntico gasta
#: otros 45 minutos para llegar al mismo lugar.
TRANSITORIOS = frozenset({"timed-out", "killed"})

#: Tope de reintentos. Uno: es un tope de costo, no una política de resiliencia.
#: Cada reintento son hasta 45 minutos de reloj y tokens.
MAX_REINTENTOS = 1


@dataclass(frozen=True)
class Decision:
    """Qué hacer con un delegado que terminó."""

    accion: str  # "aceptar" | "reintentar" | "degradar" | "escalar"
    motivo: str
    reintento: int = 0

    @property
    def termina(self) -> bool:
        return self.accion != "reintentar"


def decidir(
    estado: str,
    exit_code: int | None,
    salida_valida: bool,
    reintentos_hechos: int = 0,
) -> Decision:
    """La cadena, en un solo lugar y testeable sin lanzar nada.

    El orden importa. Un delegado que completó pero produjo algo que no era lo
    pedido no es un éxito: degrada, porque el operador necesita saber que corrió
    y salió mal antes que creer que salió bien.
    """
    if estado == "completed" and salida_valida:
        return Decision("aceptar", "completó y su informe cumple el esquema")

    if estado == "completed":
        return Decision(
            "degradar",
            "completó pero su informe no cumple el esquema: produjo algo que no era lo pedido",
        )

    if estado in TRANSITORIOS and reintentos_hechos < MAX_REINTENTOS:
        return Decision(
            "reintentar",
            f"terminó en «{estado}», que puede ser transitorio",
            reintento=reintentos_hechos + 1,
        )

    if estado in TRANSITORIOS:
        return Decision(
            "escalar",
            f"terminó en «{estado}» y ya se reintentó {reintentos_hechos} vez/veces",
        )

    return Decision(
        "escalar",
        f"terminó en «{estado}» (exit {exit_code}): corrió y no pudo, reintentarlo "
        "idéntico llegaría al mismo lugar",
    )


def informe_degradado(
    trace_id: str,
    issue: int | str,
    estado: str,
    exit_code: int | None,
    motivo: str,
    ultimas_lineas: str = "",
) -> dict:
    """El «algo» que el sistema produce siempre, aunque el delegado no pudo.

    Cumple el mismo esquema que un informe exitoso, así que el consumidor no
    necesita dos caminos de lectura.
    """
    return {
        "trace_id": trace_id,
        "issue": int(str(issue).lstrip("#")),
        "resultado": "no-pudo",
        "estado_del_proceso": estado,
        "exit_code": exit_code,
        "motivo": motivo,
        "generado_por": "la cadena de fallback, no por el delegado",
        "ultimas_lineas_del_log": ultimas_lineas[-2000:] if ultimas_lineas else "",
        "registrado_en": datetime.now(timezone.utc).isoformat(),
    }


def linea_de_inbox(trace_id: str, slug: str, decision: Decision, duracion: str) -> str:
    """La línea que ve el operador. Lleva el trace_id, que antes no estaba."""
    icono = {"aceptar": "✓", "degradar": "⚠", "escalar": "✗", "reintentar": "↻"}[decision.accion]
    return f"- {icono} **{slug}** `{trace_id}` {decision.accion} ({duracion}) — {decision.motivo}\n"


def escalar(delegates_dir: Path, trace_id: str, informe: dict) -> Path:
    """Deja el informe donde el operador lo va a encontrar, y lo devuelve.

    Escribir a disco es lo único que este módulo hace afuera. Nunca levanta: es
    el último eslabón de la cadena de fallback, y un fallback que falla deja al
    sistema sin producir nada, que es exactamente lo que viene a evitar.
    """
    destino = delegates_dir / f"escalado-{trace_id}.json"
    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        with destino.open("w", encoding="utf-8") as f:
            json.dump(informe, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
    except OSError:
        pass
    return destino


@dataclass
class Trazado:
    """Todo lo que un delegado lleva de trazabilidad, junto."""

    trace_id: str
    issue: int
    slug: str
    reintentos: int = 0
    eventos: list[str] = field(default_factory=list)

    @classmethod
    def para(cls, issue: int | str, slug: str) -> Trazado:
        tid = nuevo(issue)
        return cls(trace_id=tid, issue=issue_de(tid), slug=slug)

    def registrar(self, evento: str) -> None:
        self.eventos.append(f"{datetime.now(timezone.utc).isoformat()}  {evento}")

    def para_status(self) -> dict:
        """Los campos que van a `status.json`, que antes no los tenía."""
        return {
            "trace_id": self.trace_id,
            "issue": self.issue,
            "reintentos": self.reintentos,
            "eventos": list(self.eventos),
        }
