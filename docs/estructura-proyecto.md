# Estructura del Proyecto 991

> Documento consultable. Arbol completo de directorios del proyecto final.

---

```
web25-991-bloques-reciclables/
|
|-- CLAUDE.md                          # Instrucciones para el agente Claude
|-- PROJECT.yaml                       # Metadatos para Project Manager (99999)
|-- README.md                          # README publico
|-- LICENSE                            # MIT
|-- .gitignore                         # Python + Node + uv + pnpm
|
|-- pyproject.toml                     # uv workspace root (Python)
|-- uv.lock                           # Lockfile Python unificado
|-- package.json                       # pnpm workspace root (TS)
|-- pnpm-workspace.yaml                # Definicion workspaces TS
|-- pnpm-lock.yaml                     # Lockfile TS
|-- turbo.json                         # Turborepo config
|
|-- packages/
|   |
|   |-- python/                        # Packages Python (uv workspaces)
|   |   |
|   |   |-- bloque-core/              # OBLIGATORIO - minimo absoluto
|   |   |   |-- pyproject.toml
|   |   |   |-- src/
|   |   |   |   +-- bloque_core/
|   |   |   |       |-- __init__.py
|   |   |   |       |-- middleware/
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- request_id.py
|   |   |   |       |   |-- timing.py
|   |   |   |       |   +-- auth.py
|   |   |   |       |-- schemas/
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   +-- base.py        # PaginatedResponse[T], Health, Error
|   |   |   |       |-- logging/
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   +-- setup.py        # structlog + request ID
|   |   |   |       +-- health/
|   |   |   |           |-- __init__.py
|   |   |   |           +-- router.py       # /health endpoint
|   |   |   +-- tests/
|   |   |       +-- test_core.py
|   |   |
|   |   |-- bloque-auth/              # Auth completo
|   |   |   |-- pyproject.toml
|   |   |   |-- src/
|   |   |   |   +-- bloque_auth/
|   |   |   |       |-- __init__.py
|   |   |   |       |-- jwt/
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   +-- manager.py      # JWT RS256 con tenant_id
|   |   |   |       |-- rbac/
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   +-- permissions.py   # RBAC con dependencias FastAPI
|   |   |   |       |-- brute_force/
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   +-- protection.py    # Proteccion fuerza bruta (de 031)
|   |   |   |       +-- credentials/
|   |   |   |           |-- __init__.py
|   |   |   |           +-- fernet.py        # TenantCredential AES-256 (de 031)
|   |   |   +-- tests/
|   |   |       +-- test_auth.py
|   |   |
|   |   |-- bloque-multitenant/       # PostgreSQL RLS transparente
|   |   |   |-- pyproject.toml
|   |   |   |-- src/
|   |   |   |   +-- bloque_multitenant/
|   |   |   |       |-- __init__.py
|   |   |   |       |-- rls/
|   |   |   |       |   |-- __init__.py
|   |   |   |       |   |-- middleware.py    # SET LOCAL via contextvars
|   |   |   |       |   +-- setup.py         # SQL para crear policies RLS
|   |   |   |       +-- context/
|   |   |   |           |-- __init__.py
|   |   |   |           +-- tenant.py        # TenantContext contextvar
|   |   |   +-- tests/
|   |   |       +-- test_multitenant.py
|   |   |
|   |   +-- (futuros: bloque-redis, bloque-gateway, bloque-ai-rag, etc.)
|   |
|   +-- typescript/                    # Packages TypeScript (pnpm + Turborepo)
|       |
|       |-- bloque-ui/                # shadcn/ui componentes base
|       |   |-- package.json
|       |   |-- tsconfig.json
|       |   +-- src/
|       |       +-- components/
|       |
|       |-- bloque-api-client/        # Cliente HTTP + interceptors
|       |   |-- package.json
|       |   |-- tsconfig.json
|       |   +-- src/
|       |       +-- index.ts
|       |
|       +-- bloque-types/             # TypeScript types base
|           |-- package.json
|           |-- tsconfig.json
|           +-- src/
|               +-- index.ts
|
|-- templates/                         # Copier templates composables
|   |-- template-base/                # Turborepo + pnpm + uv + Docker Compose
|   |   |-- copier.yaml
|   |   +-- {{project_name}}/
|   |
|   |-- template-backend-fastapi/     # API + bloque-core + CRUD ejemplo
|   |   |-- copier.yaml
|   |   +-- {{project_name}}/
|   |
|   +-- template-frontend-nextjs/     # Dashboard + login + tenant selector
|       |-- copier.yaml
|       +-- {{project_name}}/
|
|-- examples/                          # Proyectos ejemplo funcionales
|   |-- api-simple/                   # Solo bloque-core, lo minimo
|   |   |-- main.py
|   |   +-- pyproject.toml
|   |
|   +-- saas-multitenant/            # core + auth + multitenant, completo
|       |-- main.py
|       +-- pyproject.toml
|
|-- docs/                              # Documentacion publica
|   |-- catalogo-bloques.md           # Lista completa de bloques
|   +-- recetas/                      # Combinaciones de bloques
|       |-- saas-multitenant.md
|       |-- bot-whatsapp.md
|       |-- api-simple.md
|       +-- mvp-sin-login.md
|
+-- .github/
    +-- workflows/
        +-- ci.yml                     # Lint + test Python + TS
```

---

## Notas

- `packages/python/` usa uv workspaces (cada subdirectorio es un package con su propio `pyproject.toml`)
- `packages/typescript/` usa pnpm workspaces + Turborepo (cada subdirectorio es un package con su propio `package.json`)
- `templates/` contiene Copier templates que generan proyectos nuevos importando bloques
- `examples/` son proyectos funcionales que demuestran como usar los bloques
- `docs/` es documentacion publica que se incluye en el README
