# Dos ramas, porque el gate de distribución vive en el servidor

> **Enmienda a [ADR 0014](0014-el-problema-era-la-distribucion-no-la-composicion.md).** Reemplaza su
> decisión de *"una sola rama de distribución"*. El resto del 0014 queda intacto: el reencuadre a
> distribución, las dos fases, el criterio de reversibilidad y todo lo demás.

El 0014 decidió colapsar `dev`, `stg` y `prod` en una rama, con `/awi-update` tirando de la punta y los nueve tests como gate. Al ir a implementarlo apareció que **esas dos cosas no se sostienen juntas**: si las instancias tiran de la punta de la rama, el gate no puede impedir nada. Un commit rojo se pushea, la rama avanza, y el compañero que actualiza se lo lleva. El gate sólo puede reportar después de los hechos.

Se consideró poner el gate en el cliente: que `/awi-update` consulte el estado de los checks del commit antes de avanzar y se quede en el último verde. Se descarta por tres razones. Reimplementa en código propio algo que GitHub ya hace. Requiere `gh` autenticado en la máquina de cada compañero, que es justamente la clase de dependencia que `/awi-update` existe para eliminar. Y su modo de falla no tiene buena salida: si la consulta de estado falla, o actualiza a ciegas o no actualiza nunca, y las dos son peores que no tener gate.

Decidimos **dos ramas**: `dev` es donde se trabaja, `main` es lo que reciben las instancias y la rama por defecto del repo. `main` avanza únicamente por fast-forward desde un commit de `dev` que pasó los tests. Un commit rojo no puede llegarle a nadie, y `/awi-update` vuelve a ser un `git pull` sin lógica.

## Por qué esto no es el esquema que congeló `prod`

El 0014 documentó que `prod` quedó 11 commits atrás y que `CHANGELOG.md` nunca se generó, y usó eso como argumento contra las ramas múltiples. Revisado, la causa no era el número de ramas sino **dos eslabones condicionales o manuales en serie dentro del camino de distribución**:

1. `prod` sólo avanzaba al mergear a mano un PR de release-please.
2. Ese PR sólo se generaba si el token de la GitHub App estaba configurado, porque el job dependía de `merge-to-stg`, que estaba gateado con `if: has_app == 'true'` — y cuando no lo estaba, se salteaba en silencio.

La promoción automática al verde no tiene ninguno de los dos. Y hay un dato de plataforma que la vuelve más robusta que la anterior: el ruleset del repo cubre sólo `refs/heads/stg` y `refs/heads/prod`, así que `main` no está protegida y el `GITHUB_TOKEN` normal alcanza para pushearla. **La promoción deja de depender de un secreto opcional**, que era el eslabón frágil.

## Consecuencias

- `promote` hace `git push origin <sha>:refs/heads/main`, un fast-forward puro sin commit de merge: `main` queda idéntica a un commit de `dev` que pasó los tests. Si no puede ser fast-forward, el push se rechaza y el job falla — señal de que alguien escribió en `main` por fuera de la promoción. Reemplaza al `git merge --no-ff -X theirs` del esquema viejo, que resolvía conflictos prefiriendo `dev` en silencio.
- Ningún job de promoción lleva `if:` sobre un secreto. Si falla, falla ruidoso.
- release-please apunta a `dev`, no a `main`. Así el bump de versión y la entrada de changelog viajan aguas abajo con el resto de los cambios; apuntándolo a `main`, sus commits quedarían sólo ahí y divergirían de `dev`, generando fricción en cada promoción.
- `/awi-update` conserva, como **diagnóstico y no como gate**, el reporte de cuánto atrás está `main` respecto de `dev`. La promoción anterior falló en 4 de 4 corridas durante días sin que nadie lo notara; si se vuelve a colgar, tiene que verse desde el cliente aunque el CI esté callado.
- `main` queda sin protección de rama, lo que es coherente con que nadie más deba escribirle: los compañeros son consumidores ([ADR 0014](0014-el-problema-era-la-distribucion-no-la-composicion.md)) y su acceso de lectura viene de que el repo es público. Queda el riesgo residual de que el mantenedor pushee a `main` por accidente y saltee el gate; se acepta.
- `stg` y `prod` se eliminan, pero el ruleset tiene la regla `deletion` activa sobre ambas: hay que editarlo o borrarlo antes. El ruleset se llama "Protect stg and prod (afin)" — fue copiado de otro proyecto.
