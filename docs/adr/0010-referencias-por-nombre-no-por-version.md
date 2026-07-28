# Las referencias cross-repo de AWI son por nombre, no por versión

> **Enmienda a [ADR 0009](0009-manifiestos-json-en-lugar-de-submodulos.md).** Conserva la decisión —
> nada en AWI es un submódulo— y reemplaza su fundamento. Lo que el 0009 dio como razones no
> resistía revisión, y una decisión sostenida por bugs corregibles se reabre en cuanto alguien
> nota que se corregían con dos líneas de `git config`.

El ADR 0009 le imputó tres fallas a los submódulos. Una auditoría posterior (`rabbitek/agenda/outputs/2026-07-28-arquitectura-composicion-workspace-awi.md`) reprodujo las tres en repos de prueba aislados y las adjudicó como higiene de configuración, no como propiedades de la arquitectura:

**"El operador no podía elegir sin tocar el `.gitmodules` compartido."** Refutado. `submodule.active` es un pathspec en `.git/config` —local, no compartido— que materializa un subconjunto sin modificar `.gitmodules`. La elección por operador ya existía como feature nativa.

**"El gitlink podía apuntar a la nada."** Real, pero prevenible con una línea: `push.recurseSubmodules=check` aborta el push del padre cuando el commit del hijo no está en ningún remoto. Sin la config el escenario del ADR se acepta en silencio; con la config falla ruidosamente.

**"El comando de init estaba roto."** Autoinfligido. Rompía porque el ADR 0001 decidió no versionar los gitlinks *mientras el sistema seguía usando submódulos* — residuo de una migración a medias, no una falla del mecanismo.

Lo que sí era de arquitectura, y el 0009 registró como queja menor, es el bump: tener que commitear el gitlink cada vez que cambia un hijo. La ceremonia se puede reducir (`submodule.recurse`, `push.recurseSubmodules=on-demand`) pero el tercer commit no se elimina sin eliminar el pin. **El bump es el pin funcionando.** Es el precio de la reproducibilidad, no un defecto.

Eso deja una sola pregunta, que el 0009 nunca formuló: **¿AWI necesita el pin?**

Un pin vale su costo cuando el padre compone a los hijos en un artefacto reproducible — un build, un deploy, un release. La raíz de AWI no es eso: es un workspace de conocimiento. No existe ningún artefacto cuya corrección dependa de `afin@abc123 + afin-webapp@def456`.

La auditoría de todo lo que cruza fronteras de repo en AWI lo confirma:

| Referencia | Cómo referencia | Estado intermedio |
|---|---|---|
| doc en `<org>/documentation/` → código en `<org>/codebase/<repo>/` | nombre / ruta | stale — normal y recuperable |
| `codebases.json` → repos de la org | nombre y URL | roto detectable — falla ruidosa |
| instrucciones del raíz → skills | ruta | stale |

**Ninguna referencia es por versión.** Las referencias por nombre degradan con gracia y su ruptura es detectable. Las referencias por versión exigen atomicidad, porque un SHA inexistente no es "viejo": es inválido. La necesidad de commit atómico cross-repo que se le atribuía a AWI era consecuencia de los gitlinks — los submódulos creaban el acoplamiento por versión, y el acoplamiento por versión es lo que necesita atomicidad. Miembro fantasma.

De ahí el fundamento correcto de la decisión del 0009: **AWI no compone un artefacto reproducible y no tiene ningún invariante transaccional cross-repo, así que no necesita el pin — y sin necesidad de pin, el mecanismo que lo impone es costo puro.**

## Test de falsación

Este ADR se revisa si alguien nombra un estado en el que "repo A commiteado, repo B no" sea *incorrecto* y no meramente *desactualizado*. Mientras no aparezca, la conclusión se sostiene.

## Consecuencias

- El fundamento del 0009 queda reemplazado; su decisión operativa, intacta. Nada que ver con submódulos cambia de comportamiento por este ADR.
- Se prohíbe reabrir el debate sobre la base de los tres cargos originales: están adjudicados y son de configuración.
- El "no necesitamos el pin" vale para los repos de contexto, no universalmente. Ver [ADR 0012](0012-contextos-flotan-dependencias-pinean.md), que corrige el error simétrico del 0009 — sacar el pin de todas partes, incluso de donde servía.
- Que la reproducibilidad no haga falta *hoy* es una propiedad de lo que AWI compone hoy. Si alguna vez la raíz produce un artefacto verificable, este ADR es lo primero que hay que revisar.
