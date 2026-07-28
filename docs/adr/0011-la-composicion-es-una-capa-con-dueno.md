# La composición del workspace es una capa con dueño propio

El problema de dominio de AWI nunca fue cómo anidar repositorios. El anidado es el mecanismo. El problema es:

> Componer, en una vista única y coherente para un agente que opera desde la raíz, un conjunto de unidades de información con **dueños y ciclos de vida distintos**, sin violar fronteras de propiedad que son reales y no negociables — repos separados, colaboradores distintos, permisos distintos.

De ahí sale el error de categoría que arrastran el ADR 0001 y el 0009 por igual: **se le pide a git que haga dos trabajos.** Versionar cada unidad es de git. Componer las unidades en un workspace no lo es. Los submódulos hacían que git *supiera* de la composición vía gitlinks; los clones más `.gitignore` hacen que git *no se entere*, vía exclusión. Son dos contorsiones del mismo malentendido: ninguna nombra la composición como una capa con dueño.

Decidimos nombrarla. **AWI es un sistema de composición de workspace: git versiona las partes, la capa de composición es dueña del todo.** Son tres capas, de las cuales existen dos.

**1. Declaración — los manifiestos.** Existe y está bien diseñada. El corte por propiedad (`user-submodules.json` privado y portable, `codebases.json` compartido y versionado) es lo que hace al manifiesto superior a `submodule.active`, que vive en `.git/config` y muere con la máquina.

**2. Materialización — clone más ocultamiento de frontera.** Existe, incompleta. `.gitignore` está haciendo dos trabajos distintos: *"no lo indexes"*, que es requisito de corrección —sin eso un `git add -A` se traga los hijos como embedded repos—, y *"no lo busques"*, que es accidente. El segundo cegó al agente, que es la única capacidad que AWI existe para habilitar. Git y ripgrep proveen dos archivos para dos concerns: falta el `.ignore` con las negaciones. Se verificó que la negación es quirúrgica — levanta la exclusión de los directorios de repo y sigue respetando los `.gitignore` internos de cada hijo.

**3. Proyección y gobierno.** No existe. Es la pieza faltante, y sostiene el invariante que define la frontera de agregado de AWI:

> **Toda ruta bajo la raíz pertenece a exactamente un repo, y esa pertenencia es conocible sin ejecutar git.**

Tres componentes, todos construibles sobre `plan()` de `manifest.py`, que ya devuelve los `Repo`:

- **Mapa de fronteras generado** en la raíz: ruta → repo → dueño → rama → política. Una lectura y el agente sabe dónde está parado.
- **`status` compuesto**: por repo, rama, dirty, ahead/behind, y drift entre manifiesto y disco. Reemplaza la señal que se perdió al sacar los gitlinks, y da más de la que daban.
- **Ruteo de escritura**: resolver ruta → repo dueño antes de escribir.

## Opciones consideradas

- **Volver a submódulos bien configurados.** Da gratis la visibilidad del agente y un estado compuesto parcial, y el pin donde hace falta. Descartada por dos razones: la elección del operador queda atada a `.git/config` y no es portable entre máquinas —propiedad arquitectónica que los manifiestos sí tienen— y el pin, lo único que da gratis, se necesita en un solo repo de cuatro, donde un campo del manifiesto lo resuelve mejor ([ADR 0012](0012-contextos-flotan-dependencias-pinean.md)).
- **Quedarse en `.ignore` y nada más.** Es el peor de los dos mundos y queda explícitamente descartada: se pierde la señal de estado que daban los gitlinks sin poner nada en su lugar. `.ignore` trata el síntoma —el agente no ve— y no la causa —nadie es dueño de la composición. Si es todo lo que se hace, el problema reaparece con otra cara: el agente ve los archivos, no sabe qué repo los posee, no puede reportar el estado del conjunto, y escribe en el repo equivocado.

## Consecuencias

- La decisión del ADR 0009 sólo es correcta si se construye la capa 3. Este ADR es la condición de validez de aquél.
- `.ignore` en la raíz (`!_data/`) y en cada org (`!codebase/*/`), con scaffolding en `/awi-org` y `/awi-client`. Es un artefacto derivado: una línea por frontera de repo, generable por el mismo código que crea la frontera.
- El mapa de fronteras es generado, nunca escrito a mano. Un mapa mantenido a mano miente en cuanto alguien togglea un codebase.
- Ninguno de los tres componentes está implementado. Ver [ADR 0013](0013-revision-integral-de-awi-core.md) — la implementación queda deliberadamente diferida hasta la revisión integral.
