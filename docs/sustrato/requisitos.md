# Requisitos del destino, como propiedades

Insumo para la decisión del sustrato — PRD 5
([#84](https://github.com/GuidoAmici/awi-core/issues/84)), subissues
[#103](https://github.com/GuidoAmici/awi-core/issues/103) y
[#104](https://github.com/GuidoAmici/awi-core/issues/104).

**Esto no decide nada.** Es la evidencia con la que el operador decide, y es el
único de los cinco PRDs que un agente no puede ejecutar por su cuenta.

Los requisitos están escritos como **propiedades verificables**, no como nombres
de productos. «Un cliente no puede leer datos de otro» es un requisito; «Postgres
con RLS» es una solución. Escribir el segundo en lugar del primero es cómo se
decide una arquitectura sin haberla evaluado.

## Lo que se reprodujo, y lo que no

Cada afirmación sobre lo que git no puede hacer se reprodujo en repositorios
aislados antes de darse por buena, con
[`reproducir.py`](reproducir.py). Es el criterio que el
[ADR 0013](../adr/0013-revision-integral-de-awi-core.md) identificó como faltante,
y el [ADR 0010](../adr/0010-referencias-por-nombre-no-por-version.md) es el ejemplo
de qué pasa cuando no se aplica: tres cargos contra los submódulos que resultaron
ser higiene de configuración.

**Resultado: 4 de 8 afirmaciones reproducen. Tres de las que no, cambian el
análisis.**

| Eje | ¿Reproduce? | Brecha |
|---|---|---|
| Control de acceso por cliente | **sí** | **diseño** |
| Escritura concurrente sobre el mismo dato | **sí** | **diseño** (sólo para dato estructurado) |
| Capacidad de consulta | **sí** | **diseño** |
| Trabajo sin conexión | sí (git lo da) | ninguna — capacidad **a proteger** |
| Escritura concurrente en archivos distintos | **no** | ninguna |
| Auditoría por registro | **no** | ninguna, si el registro es una línea |
| Latencia de propagación | **no** | del **mecanismo**, no del sustrato |
| Invariante del ADR 0011 | **no** se cae hoy | ninguna hoy |

## Los ejes, uno por uno

### 1. Control de acceso por cliente — brecha de diseño

**Propiedad:** un cliente no puede leer los datos de otro cliente, y esa garantía
no depende de que nadie mire donde no debe.

**Qué da git hoy:** nada a este nivel. La unidad de permiso de git es **el repo**.
`sparse-checkout` esconde un subdirectorio del árbol de trabajo —se comprobó que lo
esconde— pero basta volver a incluirlo para obtener el contenido: es comodidad, no
permiso. Un clon trae los objetos.

**Es de diseño, no de configuración.** No hay flag que lo cierre. La única forma de
expresarlo con git es **un repo por cliente**, que es lo que AWI ya hace con los Org
Workspaces — y funciona, mientras un cliente sea un repo entero.

**Cuándo se rompe:** cuando el dato de dos clientes tiene que convivir en la misma
consulta. Un tablero que compara métricas entre clientes necesita leer los dos, y
ahí el repo-por-cliente deja de ser una frontera y pasa a ser un obstáculo.

### 2. Escritura concurrente — brecha de diseño para el dato estructurado

**Propiedad:** dos personas modifican datos distintos al mismo tiempo y nadie
resuelve nada a mano.

**Qué da git hoy:** depende de cómo esté partido el dato, y esa distinción es la que
la reproducción hizo visible.

- **Archivos distintos por autor:** funciona. Se reprodujo el escenario completo y
  los dos cambios convivieron con `pull --rebase --autostash` sin ninguna
  intervención. **No hay brecha** — es el caso que el ciclo de contexto ya cubre.
- **El mismo archivo, líneas distintas:** conflicto que alguien resuelve a mano. El
  push se rechaza y el rebase se detiene.

**La brecha real es más chica de lo que parecía:** no es «git no soporta escritura
concurrente», es «git no soporta escritura concurrente **sobre filas del mismo
archivo**». Un archivo por registro la elimina; una tabla en un archivo la garantiza.

### 3. Capacidad de consulta — brecha de diseño

**Propiedad:** responder «todas las facturas de más de 100k de este trimestre» en
tiempo proporcional al resultado, no al total.

**Qué da git hoy:** nada. Se reprodujo con 200 registros en archivos JSON: filtrar
exigió abrir y parsear los 200. Git indexa por ruta y por hash de contenido, nunca
por valor de un campo. El costo es lineal en el total.

**Es de diseño.** Un índice externo sería otro sustrato adentro del primero, con dos
fuentes de verdad y el problema de mantenerlas de acuerdo.

**Cuándo importa:** cuando el volumen crece y cuando la consulta es interactiva. Con
200 registros son 5 ms y no importa. Con 200 mil, importa.

### 4. Auditoría por registro — **la brecha supuesta no existe**

**Propiedad:** saber quién cambió un registro, cuándo, y qué decía antes.

**Qué da git hoy:** más de lo que se suponía. `git blame` atribuye cada línea a su
autor y su commit, y `git log -L <n>,<n>:<archivo>` devuelve todas las revisiones por
las que pasó esa línea, **con su diff**.

Si un registro es una línea o un archivo, la auditoría por registro **ya existe**, y
es más completa que la de una tabla sin triggers: incluye el antes y el después, no
sólo el hecho del cambio.

**Dónde sí aparece la brecha:** si un registro es una fila con muchas columnas que
cambian independientemente. Ahí un commit sobre el archivo no dice qué columna se
tocó sin leer el diff.

**Conclusión:** este eje **no** es un argumento para cambiar de sustrato. Era uno de
los cuatro que la descripción del destino nombraba.

### 5. Latencia de propagación — **es del mecanismo, no del sustrato**

**Propiedad:** un cambio que hace un operador está disponible para los demás en
segundos, sin que nadie ejecute nada.

**Qué da git hoy:** el viaje completo commit → push → pull se midió en **54 ms**
sobre un remoto local. Contra un remoto en internet son segundos.

**Lo que falta no es velocidad: es que alguien dispare el pull.** Hoy lo dispara el
ciclo de contexto al abrir sesión, así que la latencia real no es la de git — es la
que hay hasta la próxima sesión.

**Esta es la distinción central del PRD**, y la reproducción la confirma: el
requisito de tiempo real es del **mecanismo de sincronización**, no del
almacenamiento. Un watcher, un pull periódico o un webhook lo cierran **sin cambiar
dónde viven los datos**. Responderlo mal produce una migración innecesaria.

### 6. Trabajo sin conexión — una capacidad a proteger

**Propiedad:** trabajar, versionar y consultar el historial sin conexión.

**Qué da git hoy:** todo. Se reprodujo: commit sin remoto configurado, con el
historial completo disponible localmente.

**Una base remota no da esto** sin construir una capa de sincronización propia — que
es reconstruir la mitad de git. **Este eje pesa en contra de migrar**, y no estaba
en la lista de requisitos del destino: apareció al enumerarlos como propiedades.

### 7. El invariante del ADR 0011 — se sostiene hoy

**Propiedad:** toda ruta bajo la raíz pertenece a exactamente un repo, y esa
pertenencia es conocible sin ejecutar git.

**Qué se reprodujo:** subir por los directorios padres buscando `.git` resuelve el
dueño de cualquier ruta sin invocar git. El invariante **se sostiene**, y es una
propiedad del filesystem, no de git.

**Cuándo se cae:** cuando un dato **deja de tener ruta** — que es exactamente lo que
pasa si vive en una fila de una tabla. La condición no es «cambiar de sustrato», es
«que parte del dato deje de ser un archivo».

## Sustrato y mecanismo de sincronización son dos preguntas

Es la confusión que el PRD pedía deshacer, y la evidencia la deshace:

| | Pregunta | Qué dice la evidencia |
|---|---|---|
| **Sustrato** | ¿dónde viven los datos? | tres brechas de diseño, todas sobre **dato estructurado multi-cliente consultable** |
| **Mecanismo** | ¿qué los mueve entre máquinas? | ninguna brecha de sustrato; el tiempo real se resuelve acá |

La intuición del operador —*«me parece más sencillo entenderlo como un filetree»*—
sale reforzada, no debilitada: **los archivos pueden seguir siendo archivos**. Lo
que la evidencia no sostiene es que puedan ser archivos **y** una base de datos
multi-cliente consultable a la vez.

## Las tres opciones, con su precio

Ninguna es «git» o «base de datos»: las dos primeras conservan los archivos.

### A. Conservar git, cerrar la brecha del mecanismo

Los datos siguen en archivos. Se agrega un disparador de sincronización —watcher o
pull periódico— para el requisito de tiempo real.

- **Cierra:** latencia de propagación, escritura concurrente (con un archivo por
  registro).
- **No cierra:** control de acceso por cliente más fino que un repo, consultas.
- **Precio:** el destino ERP multi-cliente consultable no se construye sobre esto.
- **Costo de migración:** cero. Es lo que hay.

### B. Híbrido con la frontera definida

El contexto cualitativo —agenda, documentación, decisiones— se queda en archivos.
El dato estructurado del ERP va a una base.

- **Cierra:** las tres brechas de diseño.
- **Conserva:** el trabajo sin conexión para el contexto, y el invariante del 0011
  para todo lo que siga siendo archivo.
- **Precio, y es el que hay que mirar:** la frontera. Una frontera sin definir es la
  que se filtra. El ADR tendría que decir **qué dato vive de qué lado** y **cómo se
  referencian entre sí las dos mitades** — y la referencia es la parte que se rompe.
- **Costo de migración:** medio, y **ahora es el momento más barato**: alpha, tres
  usuarios.

### C. Todo a una base

- **Cierra:** las tres brechas.
- **Pierde:** el trabajo sin conexión, el invariante del 0011, la auditoría por línea
  con diff, y el modelo mental de filetree que el operador dice que le funciona.
- **Costo de migración:** alto. Y hay que reconstruir la mitad de git para la
  sincronización.

## Lo que la evidencia recomienda mirar primero

**Que la pregunta no es «git o base» sino «cuánto de esto es dato estructurado
multi-cliente consultable».** Si la respuesta es «el ERP y nada más», la opción B con
la frontera escrita es la que menos pierde. Si es «casi todo», la C. Si es «todavía
nada, el ERP es una intención», la A, y la pregunta se reabre cuando el ERP exista.

**Que tres de los cuatro ejes que la descripción del destino nombraba no se
sostuvieron.** Auditoría por registro, latencia de propagación y el invariante del
0011 no son argumentos para migrar. Queda uno —control de acceso por cliente— más
dos que aparecieron al enumerar: consultas y el riesgo de perder el trabajo sin
conexión.

## Cómo reproducirlo

```bash
python3 docs/sustrato/reproducir.py
```

Es un **prototipo descartable y no lleva tests**, a propósito: un prototipo con
tests es una implementación con otro nombre, y ese compromiso es justo lo que hay
que evitar cuando el objetivo es poder descartarlo. Los resultados quedan en
`evidencia.json`.
