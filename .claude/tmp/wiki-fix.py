"""Apply all wiki fixes from the audit."""
import os
import re

WIKI = "D:/GitHub/GuidoAmici/newhaze-wiki"


def read(path):
    with open(os.path.join(WIKI, path), "r", encoding="utf-8") as f:
        return f.read()


def write(path, content):
    full = os.path.join(WIKI, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  WROTE: {path}")


def fix_ecosistema():
    """1a, 1b, 3c: auth, blog, environments, broken link"""
    c = read("digital/ecosistema.md")
    # Fix blog description
    c = c.replace("Blog técnico (pendiente conectar a API real)", "Blog técnico (conectado a API real)")
    # Fix website auth
    c = c.replace("Blog con mock data, auth temporal con Clerk", "Auth propio (email + OTP + JWT via newhaze-api)")
    # Fix blog status
    c = c.replace("Pendiente conectar a API real", "Conectado a API real (`/api/Blog`)")
    # Fix auth table - Website row
    c = c.replace("| Website | ⚠️ Clerk (temporal) | Migrar al auth propio de newhaze-api |",
                   "| Website | ✅ Auth propio (email + OTP + JWT) | ✓ Ya implementado |")
    # Remove completed items from "Bloqueado por auth"
    c = c.replace("| Website: migración auth | Remover Clerk, implementar auth propio, waitlist, Mercado Pago |\n", "")
    c = c.replace("| Blog: conexión a API real | Reemplazar mock data por llamadas a `/api/Blog` |\n", "")
    # Fix environments - replace 2-env table with 3-env
    old_env = """El sistema tiene dos ambientes completamente separados:

| Ambiente | Website | Learn | API | Base de datos |
|---|---|---|---|---|
| Production | `newhaze.ar` | `learn.newhaze.ar` | `api.newhaze.ar` | Supabase PROD (`rbszzkivswvqagasrvdj`) |
| Preview | `preview.newhaze.ar` | `preview.learn.newhaze.ar` | `dev.api.newhaze.ar` | Supabase TESTING (`rpgoixcgwynerezrxqhx`) |"""
    new_env = """El sistema tiene tres ambientes completamente separados:

| Ambiente | Website | Learn | API | Base de datos |
|---|---|---|---|---|
| Production | `newhaze.ar` | `learn.newhaze.ar` | `api.newhaze.ar` | Supabase PROD (`rbszzkivswvqagasrvdj`) |
| Beta | `beta.newhaze.ar` | `beta.learn.newhaze.ar` | `beta.api.newhaze.ar` | Supabase (nuevo proyecto beta) |
| Dev | `dev.newhaze.ar` | `dev.learn.newhaze.ar` | `dev.api.newhaze.ar` | Supabase TESTING (`rpgoixcgwynerezrxqhx`) |"""
    c = c.replace(old_env, new_env)
    # Fix broken link
    c = c.replace("proyectos/learn/_index", "proyectos/learn/mapa")
    write("digital/ecosistema.md", c)


def fix_contexto_sesion():
    """1c: Remove Clerk mention"""
    c = read("digital/contexto-sesion.md")
    c = c.replace(
        "Clerk instalado temporalmente (a reemplazar por auth propio).",
        "Auth propio (email + OTP + JWT via newhaze-api)."
    )
    write("digital/contexto-sesion.md", c)


def fix_roadmap():
    """1d, 1e: Mark completed items"""
    c = read("digital/roadmap.md")
    # These are likely formatted as roadmap items - need to see exact content
    # Will handle after reading
    write("digital/roadmap.md", c)


def fix_blog():
    """1f: Blog status"""
    c = read("digital/blog.md")
    c = c.replace(
        "El blog de `newhaze.ar` consume mock data local (route handlers en `/api/guides/`). Pendiente conectar a la API real.",
        "El blog de `newhaze.ar` está conectado a la API real (`GET /api/Blog`, `GET /api/Blog/{slug}`)."
    )
    write("digital/blog.md", c)


def fix_arquitectura():
    """2a, 2b: Dashboard access + environments"""
    c = read("digital/arquitectura.md")
    # Fix dashboard rule
    c = c.replace(
        '**El endpoint `/api/dashboard/*` no existe en production.** `DashboardController` retorna 404 si el host no contiene `"dev."`. No lo implementes ni lo llames desde código de producción.',
        '**El endpoint `/api/dashboard/*` requiere `role = "employee"` o `role = "developer"` en el JWT.** Retorna 403 para cualquier otro rol. No exponerlo sin autenticación.'
    )
    # Fix environments rule
    c = c.replace(
        "**Los ambientes production y preview usan bases de datos distintas.** Nunca mezcles las URLs de Supabase. Ver tabla de ambientes abajo.",
        "**Los tres ambientes (production, beta, dev) usan bases de datos Supabase distintas.** Nunca mezcles las URLs de Supabase entre ambientes."
    )
    c = c.replace(
        '**`ASPNETCORE_ENVIRONMENT=Development` solo en el servicio preview.** Production carga `appsettings.json`, preview carga `appsettings.Development.json`.',
        '**Cada ambiente tiene su propio `ASPNETCORE_ENVIRONMENT` y config file.** Production → `appsettings.json`, Beta → `appsettings.Beta.json`, Dev → `appsettings.Development.json`.'
    )
    # Fix environment table
    old_svc = """| Servicio | Production | Preview |
|---|---|---|
| Website | `newhaze.ar` | `preview.newhaze.ar` |
| Learn | `learn.newhaze.ar` | `preview.learn.newhaze.ar` |
| API | `api.newhaze.ar` | `dev.api.newhaze.ar` |
| Base de datos | Supabase `rbszzkivswvqagasrvdj` | Supabase `rpgoixcgwynerezrxqhx` |
| Dashboard | — | `deploy.newhaze.ar` |"""
    new_svc = """| Servicio | Production | Beta | Dev |
|---|---|---|---|
| Website | `newhaze.ar` | `beta.newhaze.ar` | `dev.newhaze.ar` |
| Learn | `learn.newhaze.ar` | `beta.learn.newhaze.ar` | `dev.learn.newhaze.ar` |
| API | `api.newhaze.ar` | `beta.api.newhaze.ar` | `dev.api.newhaze.ar` |
| Base de datos | Supabase `rbszzkivswvqagasrvdj` | Supabase (nuevo proyecto beta) | Supabase `rpgoixcgwynerezrxqhx` |
| Dashboard | — | — | `deploy.newhaze.ar` |"""
    c = c.replace(old_svc, new_svc)
    # Fix Render IDs
    c = c.replace("- Production: `srv-d3govmb3fgac7397kfd0`\n- Preview: `srv-d4k212ndiees73b7ujh0`",
                   "- Production: `srv-d3govmb3fgac7397kfd0`\n- Dev: `srv-d4k212ndiees73b7ujh0`\n- Beta: (nuevo servicio)")
    # Fix dashboard note
    c = c.replace(
        '`DashboardController` solo responde si `host.Contains("dev.")` — en production devuelve 404.',
        '`DashboardController` requiere `role = "employee"` o `role = "developer"` en el JWT. Retorna 403 para cualquier otro rol.'
    )
    # Add missing controllers
    c = c.replace(
        "    HealthController.cs       → /health",
        "    BlogController.cs         → /api/Blog/*\n    PriceListController.cs    → /api/PriceList\n    TopicsController.cs       → /api/topics/*\n    HealthController.cs       → /health"
    )
    # Add missing endpoints
    c = c.replace(
        "| GET | `/api/badges` | Badges ganados |",
        "| GET | `/api/badges` | Badges ganados |\n| GET | `/api/Blog` | Lista de posts del blog |\n| GET | `/api/Blog/{slug}` | Post individual |\n| GET | `/api/PriceList` | Lista de precios |\n| POST | `/api/auth/google` | Login con Google OAuth |"
    )
    # Add missing profile fields to DB table
    c = c.replace(
        "| `profiles` | `id`, `email`, `username`, `avatar_url` |",
        "| `profiles` | `id`, `email`, `username`, `avatar_url`, `role`, `role_status`, `early_access` |"
    )
    # Add new tables
    c = c.replace(
        "| `user_badges` | `user_id`, `badge_id`, `earned_at` |",
        "| `user_badges` | `user_id`, `badge_id`, `earned_at` |\n| `topic_content` | `topic_id`, `content`, `created_at` |\n| `blog_posts` | `id`, `slug`, `title`, `content`, `published_at` |"
    )
    write("digital/arquitectura.md", c)


def fix_arquitectura_backend():
    """2c-2g: Dashboard, environments, new tables/controllers/endpoints"""
    c = read("digital/arquitectura-backend.md")
    # Fix dashboard restriction
    c = c.replace(
        '**`DashboardController` solo responde si el host contiene `"dev."`** — en production retorna 404. No mover esta lógica. No exponer estos endpoints en ningún otro controller.',
        '**`DashboardController` requiere `role = "employee"` o `role = "developer"` en el JWT.** Retorna 403 para cualquier otro rol. Accesible desde cualquier hostname.'
    )
    # Fix appsettings rule
    c = c.replace(
        '**`appsettings.json` = production. `appsettings.Development.json` = preview.** La variable `ASPNETCORE_ENVIRONMENT=Development` solo existe en el servicio preview de Render (`dev.api.newhaze.ar`).',
        '**Cada ambiente tiene su propio config file.** Production → `appsettings.json`, Beta → `appsettings.Beta.json`, Dev → `appsettings.Development.json`. La variable `ASPNETCORE_ENVIRONMENT` se setea en cada servicio de Render.'
    )
    # Fix dashboard controller host check
    c = c.replace(
        """// Estos endpoints solo responden si:
if (!HttpContext.Request.Host.Value.Contains("dev."))
    return NotFound();""",
        """// Estos endpoints requieren rol employee o developer en el JWT:
// Retorna 403 si el usuario no tiene el rol requerido."""
    )
    # Add missing controllers to project structure
    c = c.replace(
        "    HealthController.cs       → /health",
        "    BlogController.cs         → /api/Blog/*\n    PriceListController.cs    → /api/PriceList\n    TopicsController.cs       → /api/topics/*\n    HealthController.cs       → /health"
    )
    # Add Google OAuth endpoint
    c = c.replace(
        '**POST `/api/auth/forgot-password`**',
        '**POST `/api/auth/google`**\n```csharp\n// Request\nrecord GoogleAuthRequest(string IdToken);\n\n// Response — 200\nrecord AuthResponse(string AccessToken, string RefreshToken, UserDto User);\n\n// Comportamiento: valida el ID token de Google, crea o vincula usuario en Supabase\n```\n\n**POST `/api/auth/forgot-password`**'
    )
    # Add new profile fields to UserDto
    c = c.replace(
        """record UserDto(
    Guid Id,
    string Email,
    string? Username,
    string? AvatarUrl,
    int TotalXp,
    int Level
);""",
        """record UserDto(
    Guid Id,
    string Email,
    string? Username,
    string? AvatarUrl,
    int TotalXp,
    int Level,
    string? Role,
    string? RoleStatus,
    bool EarlyAccess
);"""
    )
    # Add new profile fields to DB schema
    c = c.replace(
        "avatar_url  text  NULLABLE",
        "avatar_url  text  NULLABLE\nrole        text  NULLABLE     -- employee, consumer, growshop, distributor\nrole_status text  NULLABLE     -- pending, verified, rejected\nearly_access boolean DEFAULT false"
    )
    # Add new tables to DB schema
    c = c.replace(
        "-- user_badges",
        "-- topic_content\ntopic_id    int   PRIMARY KEY\ncontent     text  NOT NULL\ncreated_at  timestamptz\n\n-- blog_posts\nid          uuid  PRIMARY KEY\nslug        text  UNIQUE NOT NULL\ntitle       text  NOT NULL\ncontent     text  NOT NULL\npublished_at timestamptz\n\n-- user_badges"
    )
    # Fix environments table
    old_env_be = """| Variable | Production | Preview |
|---|---|---|
| `ASPNETCORE_ENVIRONMENT` | *(no seteada)* | `Development` |
| `ConnectionStrings__Supabase` | URL Supabase PROD | URL Supabase TESTING |
| Render service ID | `srv-d3govmb3fgac7397kfd0` | `srv-d4k212ndiees73b7ujh0` |"""
    new_env_be = """| Variable | Production | Beta | Dev |
|---|---|---|---|
| `ASPNETCORE_ENVIRONMENT` | `Production` | `Beta` | `Development` |
| `ConnectionStrings__Supabase` | URL Supabase PROD | URL Supabase BETA | URL Supabase TESTING |
| Config file | `appsettings.json` | `appsettings.Beta.json` | `appsettings.Development.json` |
| Render service ID | `srv-d3govmb3fgac7397kfd0` | (nuevo servicio) | `srv-d4k212ndiees73b7ujh0` |"""
    c = c.replace(old_env_be, new_env_be)
    write("digital/arquitectura-backend.md", c)


def fix_arquitectura_frontend():
    """2h: Add new profile fields to API response"""
    c = read("digital/arquitectura-frontend.md")
    c = c.replace(
        """  total_xp: number,
  level: number        // 0 = sin certificar, 1-4 = nivel certificado
}""",
        """  total_xp: number,
  level: number,       // 0 = sin certificar, 1-4 = nivel certificado
  role: string | null,        // employee, consumer, growshop, distributor
  role_status: string | null, // pending, verified, rejected
  early_access: boolean
}"""
    )
    write("digital/arquitectura-frontend.md", c)


def fix_index():
    """3a: Fix broken link"""
    c = read("_index.md")
    c = c.replace("proyectos/learn/_index", "proyectos/learn/mapa")
    write("_index.md", c)


def create_migration_plan():
    """3d: Create skeleton"""
    content = """---
tipo: proyecto
capa: datos
descripcion: Plan de migración de datos desde Google Sheets a Supabase.
links: [proyectos/mercasoft-entidades, digital/roadmap]
tags: [migracion, supabase, datos]
---

# Migración Google Sheets → Supabase

## Objetivo

Migrar los datos operativos actualmente en Google Sheets a tablas Supabase, unificando la fuente de verdad del negocio.

## Datos a migrar

| Fuente actual | Descripción |
|---|---|
| Google Sheets — Productos | Catálogo completo de productos New Haze |
| Google Sheets — Distribuidores | Red de distribuidores con datos de contacto |
| Google Sheets — Ventas | Historial de ventas/pedidos |

## Tablas destino (planificadas)

Ver entidades de referencia en [[proyectos/mercasoft-entidades]].

Las tablas `products`, `distributors` y `sales_history` están planificadas pero no creadas en Supabase. El schema final se definirá durante la implementación, tomando como base las entidades de MercaSoft.

## Estado

No iniciado. Bloqueado por finalización del sistema de auth unificado.

## Dependencias

- Auth unificado (en curso)
- Definición final de schema en Supabase
- Panel Interno operativo (para CRUD de los datos migrados)

---

→ Entidades MercaSoft: [[proyectos/mercasoft-entidades]]
→ Roadmap: [[digital/roadmap]]
"""
    write("proyectos/migracion-sheets-supabase.md", content)


def fix_tabla_nivel_3():
    """3e: Clarify checkmarks"""
    c = read("proyectos/learn/contenido/tabla-nivel-3.md")
    c = c.replace(
        "## Tabla de posts",
        "> **Nota:** Los ✅ en la columna Estado indican que el contenido está definido/escrito, no que esté implementado en la app.\n\n## Tabla de posts"
    )
    write("proyectos/learn/contenido/tabla-nivel-3.md", c)


def fix_tabla_nivel_4():
    """3f: Clarify checkmarks"""
    c = read("proyectos/learn/contenido/tabla-nivel-4.md")
    c = c.replace(
        "## Tabla de posts",
        "> **Nota:** Los ✅ en la columna Estado indican que el contenido está definido/escrito, no que esté implementado en la app.\n\n## Tabla de posts"
    )
    write("proyectos/learn/contenido/tabla-nivel-4.md", c)


if __name__ == "__main__":
    print("Applying wiki fixes...")
    print("\n[Agent 1] Auth & Blog refs:")
    fix_ecosistema()        # 1a, 1b, 3c
    fix_contexto_sesion()   # 1c
    # fix_roadmap needs manual inspection first
    fix_blog()              # 1f

    print("\n[Agent 2] Architecture docs:")
    fix_arquitectura()          # 2a, 2b
    fix_arquitectura_backend()  # 2c-2g
    fix_arquitectura_frontend() # 2h

    print("\n[Agent 3] Links & minor:")
    fix_index()             # 3a
    create_migration_plan() # 3d
    fix_tabla_nivel_3()     # 3e
    fix_tabla_nivel_4()     # 3f

    print("\nDone! Roadmap (1d, 1e) needs manual review — reading now...")
    print("\n--- roadmap.md content ---")
    print(read("digital/roadmap.md"))
