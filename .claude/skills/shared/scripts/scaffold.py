"""Crear el árbol de una organización, y registrarla en el manifiesto.

Esta lógica vivía cuatro veces. `awi-client`, `awi-org`, `new-client` e
`initialize` eran la misma skill de scaffolding, y tres de sus scripts eran copias
**byte-idénticas**: `init_org.py` ≡ `init_client.py`, más `import_client.py` y
`toggle_client.py` duplicados.

**Organización y cliente son la misma cosa.** El PRD 4 pedía determinarlo antes de
unificar, porque el vocabulario del dominio los distinguía. No los distingue:
`CONTEXT.md` define **Org Workspace** y no define «cliente» como término aparte, y
`_data/entities/` —la ruta que usaba la versión «cliente»— ya no existe. Los
scripts idénticos no eran el bug: eran la evidencia.

El corte es el mismo que ya funciona bien en `manifest.py`: mecánica acá, decisión
en el llamador. Las skills quedan como envoltorios finos.

**Idempotente**: correrlo dos veces no rompe ni duplica. Es lo que hace seguro
reintentar un scaffolding que se cortó a mitad de camino, que es exactamente
cuando alguien lo vuelve a correr.

Ver PRD 4 (issue #83), subissues #99 y #100.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from paths import ORGANIZATIONS_RELDIR, USER_SUBMODULES_FILE

#: Subdirectorios de `agenda/`. El orden es el del documento que los describe.
AGENDA_FOLDERS = (
    "tasks", "projects", "people", "companies", "ideas",
    "daily", "weekly", "outputs", "deliverables", "handoffs", "planning",
    "user-profile-inference",
)

AGENDA_ABSTRACT = (
    "Lo que pasó o falta que pase en esta organización: tareas, proyectos, "
    "relaciones, diario, análisis y entregas. Fechado; envejece solo.\n"
)

AGENDA_OVERVIEW = """\
Agenda de este workspace: lo que pasó o falta que pase. Va fechado, se acumula
y envejece solo. Lo que es verdad hoy y se mantiene al día va a documentation/.

## Estructura

- tasks/        — unidades atómicas de trabajo
- projects/     — iniciativas con plazo; su bitácora va en el archivo del proyecto
- people/       — perfiles de personas y seguimientos
- companies/    — empresas con las que hay relación: clientes, proveedores
- ideas/        — exploración y modelos mentales
- daily/        — notas diarias (YYYY-MM-DD.md)
- weekly/       — revisiones semanales (YYYY-WNN.md)
- outputs/      — análisis, investigaciones e informes fechados (YYYY-MM-DD-<slug>.md).
                  Una decisión vigente no va acá: va a documentation/adr/ o bdr/
- deliverables/ — piezas entregadas o publicadas a un tercero: propuestas,
                  listas de precios, guiones (YYYY-MM-DD-<slug>)
- handoffs/     — traspasos entre sesiones; los consumidos van a handoffs/consumidos/
- planning/     — objetivos trimestrales y anuales
- user-profile-inference/ — observaciones de sesión

Todos los archivos usan frontmatter YAML. Ver ADR 0027 y file-formats.md en AWI.
"""

DOCUMENTATION_ABSTRACT = (
    "Lo que es verdad hoy en esta organización: perfil, marca, procedimientos, "
    "productos y decisiones vigentes. Se mantiene al día.\n"
)

DOCUMENTATION_OVERVIEW = """\
Documentación de este workspace: lo que es verdad hoy. Se sobrescribe cuando
cambia y se lee para actuar. Lo fechado —lo que pasó, lo que se entregó— va a
agenda/.

## Cómo se ordena

Por tema permanente, nunca por proyecto: el proyecto termina y lo que se supo
sigue valiendo. El proyecto vive en agenda/projects/; lo que se sabe del
producto, en documentation/productos/<producto>/.

- org-profile.md — misión, visión y valores
- _index.md      — mapa de esta carpeta
- _glosario.md   — términos del dominio
- adr/           — decisiones de arquitectura vigentes (NNNN-<slug>.md)
- bdr/           — decisiones de negocio vigentes (NNNN-<slug>.md)
- identidad/     — marca, Design System y tokens. Se quedan acá aunque haya
                   código que los use: cualquiera que trabaje la org tiene que
                   poder leerlos
- productos/, operaciones/, ventas/, legal/ … — una carpeta por tema

Lo que lleva package.json, scripts de build o dependencias es un codebase, no
documentación.

## Cambios

Cada documento cierra con una sección `## Cambios`: una línea por cambio de
fondo, con fecha, qué era y qué es, y el enlace a la decisión que lo causó.
Erratas no. Ver ADR 0027 en AWI.
"""

CLAUDE_MD = """\
# {titulo} — Org Workspace de AWI

Workspace de una organización, gestionado por AWI. Las reglas, la estructura, la
taxonomía y los comandos están en el repo de AWI, no acá.

Este repo es un **clon aparte**, no un submódulo: nada en AWI lo es. Se materializa
por `git clone` desde lo que declara el manifiesto del operador.

## Estructura

- **Agenda:** `agenda/` — lo fechado, que envejece: tareas, proyectos, relaciones,
  diario, análisis y entregas
- **Documentación:** `documentation/` — lo vigente, que se mantiene: perfil, marca,
  procedimientos, productos y decisiones (`adr/`, `bdr/`)
- **Codebase:** `codebase/` — cada repo de código, su propio clon
- **Manifiesto:** `codebases.json` — de qué repos está hecha esta organización

## Fecha actual

Desde la raíz de AWI:
```bash
bash .claude/hooks/get-datetime.sh full
```
"""

CODEBASES_JSON = {
    "_comment": (
        "Manifiesto versionado: de qué repos está hecha esta organización, y en qué "
        "rama. Lo comparten todos los que trabajan la org. Qué codebases baja cada "
        "operador es su decisión privada y vive en su user-submodules.json — el corte "
        "es el punto. Ver ADR 0009."
    ),
    "codebases": {},
}

GITIGNORE = """\
# Obsidian
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/plugins/
.obsidian/core-plugins-migration.json

# macOS
.DS_Store

# Temporary files
*.tmp

# Cada codebase es un clon aparte: sin esto, `git add -A` se los tragaría como
# repos embebidos. Es un requisito de corrección, no higiene.
codebase/*/
"""


class ScaffoldFallido(RuntimeError):
    pass


@dataclass
class Resultado:
    path: Path
    creado: bool
    #: Qué se hizo, para que el llamador lo reporte sin adivinar.
    acciones: list[str]
    registrado: bool = False


def _git(cwd: Path, *args: str) -> None:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise ScaffoldFallido(f"git {' '.join(args)} falló en {cwd}: {r.stderr.strip()}")


def _titulo(nombre: str) -> str:
    return nombre.replace("-", " ").title()


def crear_arbol(nombre: str, destino: Path) -> Resultado:
    """Crea la estructura y el repo. Idempotente: lo que ya está no se toca.

    Devuelve qué hizo. Un scaffolding que dice «listo» sobre un directorio que ya
    existía y no tocó deja al llamador sin saber si creó algo.
    """
    path = (destino / nombre).resolve()
    acciones: list[str] = []
    ya_estaba = path.exists()

    for folder in AGENDA_FOLDERS:
        (path / "agenda" / folder).mkdir(parents=True, exist_ok=True)
    (path / "documentation").mkdir(parents=True, exist_ok=True)
    (path / "codebase").mkdir(parents=True, exist_ok=True)

    archivos = {
        path / "agenda" / ".abstract.md": AGENDA_ABSTRACT,
        path / "agenda" / ".overview.md": AGENDA_OVERVIEW,
        path / "documentation" / ".abstract.md": DOCUMENTATION_ABSTRACT,
        path / "documentation" / ".overview.md": DOCUMENTATION_OVERVIEW,
        path / "CLAUDE.md": CLAUDE_MD.format(titulo=_titulo(nombre)),
        path / ".gitignore": GITIGNORE,
        path / "codebases.json": json.dumps(CODEBASES_JSON, ensure_ascii=False, indent=2) + "\n",
    }
    for archivo, contenido in archivos.items():
        if not archivo.exists():
            archivo.write_text(contenido, encoding="utf-8")
            acciones.append(f"creado {archivo.relative_to(path)}")

    if not (path / ".git").exists():
        _git(path, "init", "-q")
        _git(path, "add", "-A")
        _git(path, "commit", "-qm", f"chore({nombre}): inicializar el workspace")
        acciones.append("repo inicializado con su primer commit")
    elif acciones:
        acciones.append("hay cambios sin commitear en el repo existente")

    if ya_estaba and not acciones:
        acciones.append("ya estaba completo: no se tocó nada")

    return Resultado(path=path, creado=not ya_estaba, acciones=acciones)


def registrar(
    nombre: str,
    url: str,
    manifiesto: Path,
    branch: str = "main",
    tipo: str = "org-workspace",
) -> bool:
    """Declara la entrada en el manifiesto del operador. Idempotente.

    Devuelve True si la agregó, False si ya estaba. Sin esto, el árbol existe en
    disco y nadie lo materializa en otra máquina: el manifiesto es lo que hace
    que un repo exista para AWI.
    """
    try:
        datos = json.loads(manifiesto.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise ScaffoldFallido(f"no existe el manifiesto {manifiesto}: ¿corriste /awi-user?") from e
    except json.JSONDecodeError as e:
        raise ScaffoldFallido(f"{manifiesto} no es JSON válido: {e}") from e

    # Las entradas van en la raíz del JSON, no envueltas en una clave. Es como
    # las lee `manifest.active_entries()`, que es lo que decide qué se
    # materializa: un envoltorio las volvería invisibles para el sistema.
    if nombre in datos:
        return False

    datos[nombre] = {
        "url": url,
        "path": f"{ORGANIZATIONS_RELDIR}/{nombre}",
        "branch": branch,
        "type": tipo,
        "active": True,
        "codebases": {},
    }
    manifiesto.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True


def scaffold(
    nombre: str,
    destino: Path,
    url: str | None = None,
    manifiesto: Path | None = None,
    branch: str = "main",
) -> Resultado:
    """Crear el árbol y, si hay a dónde, registrarlo. La operación completa.

    Registrar es opcional a propósito: crear el árbol sin remoto es un paso
    legítimo —el repo de GitHub puede no existir todavía— y fallar ahí obligaría a
    rehacer el scaffolding cuando el remoto aparezca.
    """
    resultado = crear_arbol(nombre, destino)
    if url and manifiesto:
        resultado.registrado = registrar(nombre, url, manifiesto, branch)
        resultado.acciones.append(
            "registrado en el manifiesto" if resultado.registrado
            else "ya estaba en el manifiesto"
        )
    return resultado


def describir(resultado: Resultado, nombre: str) -> str:
    lineas = [f"{'Creado' if resultado.creado else 'Actualizado'} «{nombre}» en {resultado.path}", ""]
    lineas += [f"  · {a}" for a in resultado.acciones]
    lineas += [
        "",
        "Estructura:",
        f"  agenda/         {', '.join(AGENDA_FOLDERS[:4])}, …",
        "  documentation/  estilo de escritura, perfil, wiki",
        "  codebase/       cada codebase, su propio clon",
        "  codebases.json  el manifiesto compartido de la org",
    ]
    if not resultado.registrado:
        lineas += [
            "",
            f"Todavía no está en el {USER_SUBMODULES_FILE} de nadie: hasta que lo esté,",
            "ninguna otra máquina lo va a materializar.",
        ]
    return "\n".join(lineas)
