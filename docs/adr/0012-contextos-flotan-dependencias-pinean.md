# Contextos flotan, dependencias pinean

El ADR 0009 aplicó una sola política de versionado —*seguir la punta de la rama declarada*— a todas las entradas del manifiesto. Pero `user-submodules.json` declara dos clases de cosa que no son la misma:

```json
"afin":          { "type": "org-workspace", "url": ".../GuidoAmici/afin-workspace.git" }
"agency-agents": { "type": "system-repo",   "url": ".../msitarzewski/agency-agents.git" }
```

| | Org workspaces (`newhaze`, `rabbitek`, `afin`) | `agency-agents` |
|---|---|---|
| Dueño | propio o del cliente | **un tercero** (`msitarzewski`) |
| Qué es | **contexto** — datos sobre los que se trabaja | **dependencia** — comportamiento que se ejecuta |
| Efecto de un cambio upstream | no hay upstream ajeno | **cambia cómo actúan los agentes** |
| Política correcta | flotar en la rama | **pinnear** |

Para los contextos, flotar es correcto: son datos propios, y su punta es siempre lo que se quiere. Para `agency-agents` es incorrecto. Cada `/awi-sync` trae al sistema que define el comportamiento de los agentes lo que un tercero haya pusheado a `main`, sin revisión y sin reproducibilidad. Un rename upstream de un archivo de rol rompe una skill en silencio.

El diseño ya reconoce a medias que son categorías distintas: `Repo` tiene el campo `upstream` y `agency-agents` lo declara `true`. Pero la política que ese campo aplica hoy es *"nunca pushear"*, no *"pinnear"* — la mitad correcta del reconocimiento, con la conclusión equivocada.

Decidimos separar las dos políticas por categoría. Las entradas `system-repo` admiten un campo **`rev`** en el manifiesto: un commit o tag al que se materializa el repo, en lugar de la punta de la rama. Actualizar el `rev` es un acto explícito y revisable, no un efecto lateral de sincronizar.

Aquí es donde el pin sí hace falta — y no hace falta un gitlink para tenerlo. Un campo del manifiesto lo resuelve con grano fino, que es precisamente lo que un manifiesto hace bien y lo que los submódulos hacían con grano grueso.

**Diagnóstico de fondo:** los submódulos no estaban mal por ser submódulos, sino por imponer una política única a categorías con necesidades opuestas. El ADR 0009 cometió el error simétrico — sacó el pin de todas partes, incluso de donde servía. Este ADR corrige la mitad que faltaba.

## Consecuencias

- `materialise_target()` en `manifest.py` debe soportar checkout de un `rev` además de `--branch`. Un repo pinneado que ya está en disco en otro commit es drift y lo reporta el `status` compuesto ([ADR 0011](0011-la-composicion-es-una-capa-con-dueno.md)), no lo corrige la materialización en silencio.
- `/awi-sync` no mueve un repo pinneado. Hoy hace fast-forward a upstream sobre `agency-agents`; con `rev` presente, eso pasa a ser una operación aparte y deliberada.
- `rev` es opcional. Una entrada `system-repo` sin `rev` flota, con el mismo comportamiento de hoy — el ADR habilita el pin, no lo impone retroactivamente.
- La categoría, no el nombre del repo, decide la política. Si mañana un `org-workspace` pasa a contener comportamiento ejecutable, cambia de categoría o se parte.
- No está implementado. Ver [ADR 0013](0013-revision-integral-de-awi-core.md).
