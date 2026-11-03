# Una sola rama: `main`

> **Estado: aceptado (2026-11-03).** Lo pidió el operador. Reemplaza al
> [ADR 0015](0015-dos-ramas-porque-el-gate-vive-en-el-servidor.md).

## La decisión

`awi-core` tiene una sola rama de larga vida, `main`: ahí se trabaja y eso reciben las instancias. `dev` se eliminó después de que `main` avanzara hasta su punta por el fast-forward de siempre, con el CI en verde.

## Lo que se pierde

El [ADR 0015](0015-dos-ramas-porque-el-gate-vive-en-el-servidor.md) separó las ramas por un argumento que sigue siendo cierto: si las instancias tiran de la punta de la rama, el gate no puede impedir nada. **Un push directo a `main` con tests rojos le llega a quien corra `/awi-update`.** La decisión acepta ese costo; no lo resuelve.

Entre el 2026-10-11 y el 2026-11-03 el gate retuvo 20 commits de `dev` por dos tests que leían un archivo en `.gitignore`. Ningún commit rojo llegó a las instancias, y tampoco ninguno de los 20. Esa retención deja de existir.

## Consecuencias

- El CI corre en cada push y cada PR a `main`. El job `promote` desaparece. Un cambio que deba pasar los tests antes de llegarle a alguien va por PR.
- release-please apunta a `main`. La rama de su PR y las de cada PR son temporales: «una sola rama» habla de las de larga vida.
- `/awi-update` deja de reportar cuántos commits le faltan a `main`, porque ya no hay contra qué medir.
- En `main` `/awi-update` sigue siendo un reset duro, y ahora también corre donde trabaja el mantenedor. Sus commits sin pushear no se pierden: van a una rama `respaldo/`.
- Una instancia que haya quedado sobre `dev` deja de recibir actualizaciones hasta que pase a `main`.
