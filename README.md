# AWI — Agentic Workflow Integrator

> Gestor de contexto empresarial para Claude Code.

AWI ordena en un filetree de git la agenda, la documentación y las decisiones de cada organización con la que trabajás, y las deja al alcance de la sesión donde tomás la decisión. Es una fábrica de sistemas: el mismo motor opera tu espacio personal y el de cada empresa o cliente, cada uno en su propio repo.

Lo que lo distingue de una carpeta de notas es que **el agente sabe dónde va cada cosa**. Las reglas de esa distribución viven en [CLAUDE.md](CLAUDE.md), que es la fuente de verdad, y lo que sólo aplica a una parte del trabajo vive en [docs/agents/](docs/agents/).

---

## Qué hace

- **Captura y archiva.** `/new reunión con Sara el viernes sobre el Q2` crea la nota de persona, la tarea y el enlace al proyecto en el workspace que corresponde.
- **Planifica.** `/today`, `/week`, `/quarter` y `/year` arman el plan desde lo que vence y lo que está activo, y `/wrap-session` cierra la sesión dejando los hilos abiertos anotados.
- **Trabaja el tracker.** Los issues viven en GitHub, distribuidos por alcance: el repo del codebase, el workspace de la org, o `my-awi-user` para lo que cruza organizaciones. `/triage` los mueve por la máquina de estados y `/delegate-issue` despacha los que quedaron listos.
- **Sincroniza el contexto entre operadores.** Traer y publicar las agendas de org no se pregunta: está anclado como paso de las skills que abren y cierran cada momento.

---

## Requisitos

| | Para qué |
|---|---|
| [Claude Code](https://claude.com/claude-code) | El agente que lo opera |
| Git | El sustrato: todo es un repo |
| Python 3.11+ | Los scripts que hacen la mecánica determinística |
| [`gh` CLI](https://cli.github.com/), autenticado | Identidad e issues. `gh auth status` tiene que responder |

---

## Instalación

```bash
git clone https://github.com/GuidoAmici/awi-core.git awi && \
cd awi && \
claude
```

Y adentro de la sesión:

```
/awi-introduction
```

Es un solo comando: explica qué es AWI, vincula tu cuenta de GitHub, toma tus preferencias, scaffoldea el repo y te deja en `/today`. Después, `/awi-initialize` clona todo lo que tu manifiesto declare.

### El plugin de formato

Las reglas de **cómo escribe el agente** salieron a un plugin aparte, porque valen en cualquier sesión y no sólo acá:

```
/plugin marketplace add GuidoAmici/awi-core
/plugin install answerable@awi
```

Ver [`plugins/answerable/`](plugins/answerable/).

---

## Comandos

30 skills. La lista completa, agrupada por momento de uso, está en
[`tables/skills.md`](_system/_agentic-workflow-integrator/tables/skills.md).

El día típico son cuatro: `/today` para abrir, `/new` durante, `/break` para cortar, `/wrap-session` para cerrar.

---

## Cómo está hecho

| Pieza | Dónde | Qué hace |
|---|---|---|
| Reglas | [CLAUDE.md](CLAUDE.md) | Fuente de verdad. Lo que rige en toda sesión |
| Reglas por rama | [docs/agents/](docs/agents/) | Tracker, worktrees, contexto compartido, Docker, delegación, decisiones |
| Skills | `.claude/skills/` | Un directorio por comando, con sus scripts al lado |
| Mecánica | `.claude/skills/shared/scripts/` | Lo determinístico —sync, manifiestos, scaffolding, escaneo de material sensible— con tests |
| Hooks | `.claude/hooks/` | Autenticación de `gh`, guard de worktrees, aviso de delegados terminados |
| Decisiones | [docs/adr/](docs/adr/) | 22 ADRs. El registro de por qué el sistema es como es |
| Dominio | [CONTEXT.md](CONTEXT.md) | El glosario: qué significa cada término y cuáles están prohibidos |

**El juicio va en las instrucciones y la mecánica en el código.** Cuándo pullear o cómo nombrar un commit es juicio y vive en markdown; pullear, abortar limpio ante un conflicto y reportar es mecánica y vive en Python con tests. La razón es empírica: una instrucción en prosa se cumple a veces, y para traer el contexto de otra persona «a veces» significa trabajar sobre datos viejos sin enterarse.

---

## Estructura

```
awi/
├── CLAUDE.md            # Las reglas — fuente de verdad
├── CONTEXT.md           # El glosario del dominio
├── _data/               # Datos del operador — gitignoreado, un repo por entrada
│   ├── users/<github-id>/            # Agenda, documentación, manifiesto privado
│   └── organizations/<nombre>/       # agenda/ documentation/ codebase/
├── _system/             # Documentación del framework
├── docs/                # adr/ decisiones · agents/ reglas por rama
├── plugins/answerable/  # El plugin de formato de respuesta
└── .claude/             # skills/ hooks/ rules/ settings.json
```

Cada entrada de `_data/` es **un clon de git aparte**, declarado en `user-submodules.json` y materializado por `git clone`. Nada acá es un submódulo — ver [ADR 0009](docs/adr/0009-manifiestos-json-en-lugar-de-submodulos.md). Que `_data/` esté en `.gitignore` es un requisito de corrección y no higiene: sin eso, un `git add -A` en la raíz se traga los hijos como repos embebidos.

---

## Desarrollo

```bash
python3 -m pytest -q tests && \
python3 .claude/skills/shared/scripts/vocab_check.py
```

240 tests y un chequeo de vocabulario que falla si un documento reintroduce un término que describe un mecanismo eliminado. Los dos corren en CI sobre `dev`; `main` es la rama que reciben las instancias y sólo avanza desde un commit que pasó ([ADR 0015](docs/adr/0015-dos-ramas-porque-el-gate-vive-en-el-servidor.md)).

Toda decisión de arquitectura se registra como ADR en [docs/adr/](docs/adr/) antes de implementarse.

---

## Licencia

MIT.
