"""Perfil de ejecución de un delegado: con qué arranca, declarado como dato.

El lanzador construía su línea de comandos con constantes, así que la política de
acceso estaba enterrada en el mecanismo. Acá la política es dato: qué servidores
MCP, qué flags y qué tope de reloj. El lanzador queda como mecanismo.

Lo que esto corta es concreto. Un delegado heredaba la configuración MCP completa
del operador —doce servidores, entre ellos doppler (secretos), supabase (base de
producción), mercadopago (pagos) y gmail (envío de correo)— y corría **desatendido**
con `--dangerously-skip-permissions`, que además anula la única regla `deny` que
el sistema declara. Su prompt sale de un comentario de issue de GitHub: contenido
externo y editable.

Se **conserva** la ejecución desatendida, que es el punto entero de delegar:
quitar `--dangerously-skip-permissions` cuelga al delegado en el primer prompt de
permisos porque no hay nadie para aprobarlo. Lo que cambia es lo que ese flag
habilita. Saltear permisos sobre un servidor de issues es defendible; saltearlos
sobre doce con credenciales de producción no.

Ver PRD 2 (issue #81), subissues #90 y #91.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

#: Dónde viven los perfiles y sus configuraciones MCP, relativo a la raíz de AWI.
PERFILES_RELDIR = ".claude/delegate-profiles"
PERFILES_ARCHIVO = f"{PERFILES_RELDIR}/profiles.json"

#: El perfil que se usa cuando el despacho no elige. Es el más restrictivo a
#: propósito: olvidarse de elegir tiene que fallar del lado seguro.
POR_DEFECTO = "minimo"

#: Servidores que ningún proceso desatendido debería alcanzar sin decisión
#: explícita. La lista está acá y no sólo en los datos para que el test pueda
#: aseverar sobre ella: es la afirmación que el PRD quiere verificable.
SENSIBLES = frozenset({"doppler", "supabase", "mercadopago", "gmail", "vercel", "notion"})

#: Tope de reloj por defecto. Ya existía en el lanzador desde 9f4b575; el perfil
#: lo absorbe como uno de sus campos en vez de ser un parámetro suelto.
TIMEOUT_POR_DEFECTO_S = 45 * 60


class PerfilInvalido(ValueError):
    """Perfil inexistente o mal declarado. Ruidoso: no cae al comportamiento heredado."""


@dataclass(frozen=True)
class Perfil:
    nombre: str
    descripcion: str
    #: Ruta al archivo de configuración MCP, relativa a la raíz de AWI.
    mcp_config: str
    servidores: tuple[str, ...]
    flags: tuple[str, ...]
    timeout_s: int = TIMEOUT_POR_DEFECTO_S

    @property
    def alcanza_algo_sensible(self) -> tuple[str, ...]:
        """Los servidores sensibles que este perfil habilita. Vacío es lo esperado."""
        return tuple(sorted(SENSIBLES & set(self.servidores)))

    def linea_de_comandos(self, awi_root: Path) -> list[str]:
        """Los argumentos que el lanzador agrega por el perfil.

        `--strict-mcp-config` es la pieza que corta la herencia: sin él, la
        configuración del operador se suma a la que se pasa, y pasar una
        configuración mínima no quitaría nada.
        """
        return ["--mcp-config", str(awi_root / self.mcp_config), "--strict-mcp-config", *self.flags]


@dataclass
class Catalogo:
    perfiles: dict[str, Perfil] = field(default_factory=dict)

    def __getitem__(self, nombre: str) -> Perfil:
        if nombre not in self.perfiles:
            raise PerfilInvalido(
                f"no hay perfil «{nombre}». Los declarados son: "
                f"{', '.join(sorted(self.perfiles))}."
            )
        return self.perfiles[nombre]

    def por_defecto(self) -> Perfil:
        return self[POR_DEFECTO]


def cargar(awi_root: Path, archivo: str | Path | None = None) -> Catalogo:
    """Lee los perfiles declarados.

    Falla ruidosamente ante un archivo ausente o mal formado, y ante la ausencia
    del perfil por defecto: un lanzador que no encuentra su política y arranca
    igual es exactamente el comportamiento heredado que esto viene a quitar.
    """
    ruta = Path(archivo) if archivo else awi_root / PERFILES_ARCHIVO
    try:
        crudo = json.loads(Path(ruta).read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise PerfilInvalido(f"no existe el archivo de perfiles: {ruta}") from e
    except json.JSONDecodeError as e:
        raise PerfilInvalido(f"{ruta} no es JSON válido: {e}") from e

    declarados = crudo.get("perfiles")
    if not isinstance(declarados, dict) or not declarados:
        raise PerfilInvalido(f"{ruta} no declara ningún perfil en «perfiles»")

    catalogo = Catalogo()
    for nombre, cfg in declarados.items():
        mcp_config = cfg.get("mcp_config")
        if not mcp_config:
            raise PerfilInvalido(f"perfil «{nombre}»: no declara «mcp_config»")
        catalogo.perfiles[nombre] = Perfil(
            nombre=nombre,
            descripcion=cfg.get("descripcion", ""),
            mcp_config=mcp_config,
            servidores=tuple(cfg.get("servidores", ())),
            flags=tuple(cfg.get("flags", ())),
            timeout_s=int(cfg.get("timeout_s", TIMEOUT_POR_DEFECTO_S)),
        )

    if POR_DEFECTO not in catalogo.perfiles:
        raise PerfilInvalido(
            f"{ruta} no declara el perfil por defecto «{POR_DEFECTO}»: sin él, un "
            "despacho que no elige perfil no tiene a qué caer del lado seguro."
        )
    return catalogo


def servidores_de(awi_root: Path, perfil: Perfil) -> list[str]:
    """Los servidores que el archivo de configuración MCP del perfil realmente trae.

    Se lee del archivo y no del campo `servidores` del perfil a propósito: el
    campo es la declaración y el archivo es lo que el proceso va a recibir. Si
    divergen, lo que importa es el archivo, y el test tiene que poder verlo.
    """
    ruta = awi_root / perfil.mcp_config
    try:
        crudo = json.loads(ruta.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise PerfilInvalido(
            f"perfil «{perfil.nombre}»: su mcp_config no existe: {ruta}"
        ) from e
    except json.JSONDecodeError as e:
        raise PerfilInvalido(f"perfil «{perfil.nombre}»: {ruta} no es JSON válido: {e}") from e
    return sorted(crudo.get("mcpServers", {}))


def describir(awi_root: Path, catalogo: Catalogo) -> str:
    """Los perfiles y a qué llega cada uno, para auditar de un vistazo."""
    lineas = []
    for nombre in sorted(catalogo.perfiles):
        p = catalogo.perfiles[nombre]
        try:
            reales = servidores_de(awi_root, p)
        except PerfilInvalido as e:
            reales = [f"<error: {e}>"]
        marca = " ← POR DEFECTO" if nombre == POR_DEFECTO else ""
        alerta = f"  ⚠ alcanza {', '.join(p.alcanza_algo_sensible)}" if p.alcanza_algo_sensible else ""
        lineas += [
            f"{nombre}{marca}",
            f"   {p.descripcion}",
            f"   servidores: {', '.join(reales) or '(ninguno)'}{alerta}",
            f"   tope: {p.timeout_s // 60} min · flags: {' '.join(p.flags) or '(ninguno)'}",
            "",
        ]
    return "\n".join(lineas)


def main(argv: list[str] | None = None) -> int:
    import argparse

    from paths import AWI_ROOT

    p = argparse.ArgumentParser(description="Perfiles de ejecución de los delegados.")
    p.add_argument("perfil", nargs="?", help="mostrar sólo este perfil")
    p.add_argument("--raiz", type=Path, default=AWI_ROOT)
    args = p.parse_args(argv)

    try:
        catalogo = cargar(args.raiz)
        if args.perfil:
            perfil = catalogo[args.perfil]
            print(f"{perfil.nombre}: {perfil.descripcion}")
            print(f"servidores: {', '.join(servidores_de(args.raiz, perfil))}")
            print(f"argumentos: {' '.join(perfil.linea_de_comandos(args.raiz))}")
        else:
            print(describir(args.raiz, catalogo), end="")
    except PerfilInvalido as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
