# Docker apagado lo levantás vos

Docker Desktop corre en Windows y WSL2 le habla por un named pipe. Cuando está cerrado —después de un `wsl --shutdown`, al reiniciar la máquina— todo lo que dependa de contenedores falla con `failed to connect to the docker API`: el stack local de Supabase, los tests que lo usan, el barrido de stacks.

**Eso no es un pedido para el operador.** Si necesitás Docker y está caído, levantalo:

```bash
bash .claude/hooks/docker-up.sh
```

Si ya estaba corriendo sale enseguida sin tocar nada. Si no, lanza Docker Desktop por `powershell.exe` y espera al **daemon**, no al proceso: la app abre mucho antes de que el engine acepte conexiones, y ahí está la diferencia entre creer que arrancó y que arrancó. `docker-up.sh status` responde sin levantar nada.

# Que `docker` esté en el PATH no quiere decir que la integración esté prendida

Hay dos caminos de WSL2 al engine, y se parecen lo suficiente para confundir:

| | Dónde vive el cliente | Cómo es |
|---|---|---|
| **Integración WSL** | `/usr/bin/docker` | binario Linux, habla por socket. Rápido, y es lo que esperan `supabase` CLI y testcontainers |
| **Interop** | `/mnt/c/…/resources/bin/docker` | script `sh` que cruza a Windows en cada llamada. Anda, pero es lento y traduce rutas distinto |

Los dos aparecen como `docker` en el PATH. Se distinguen por la ruta: **bajo `/mnt/c` es interop**, y entonces la integración está apagada.

El script lo detecta así y, si hace falta, la prende: escribe la distro en `IntegratedWslDistros` de `settings-store.json`. Eso se hace con Docker **cerrado** —Docker Desktop lee ese archivo al arrancar y lo pisa al salir—, así que sólo ocurre en el camino de arranque. Con Docker ya corriendo el script avisa que está apagada y no reinicia nada por su cuenta: hay contenedores vivos y bajarlos sorprendería a quien los esté usando.

Sale con 1 sólo si no arrancó dentro del timeout, que suele significar algo que sí necesita al operador: login vencido o una actualización pendiente. Recién ahí se lo pedís, diciéndole qué falló.
