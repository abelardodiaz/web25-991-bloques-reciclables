# Bloques Reciclables

Ecosistema open source de bloques de codigo reciclables. Una caja de legos multi-stack (Python + TypeScript) para construir cualquier tipo de proyecto web/API.

## Bloques Disponibles

### Python (Backend)

| Bloque | Descripcion | Status |
|--------|-------------|--------|
| `bloque-core` | Middleware, schemas, logging, health checks | MVP |
| `bloque-auth` | JWT RS256, RBAC, brute force, credential encryption | MVP |
| `bloque-multitenant` | PostgreSQL RLS transparente via contextvars | MVP |

### TypeScript (Frontend)

| Bloque | Descripcion | Status |
|--------|-------------|--------|
| `@bloque/types` | TypeScript types base (auth, pagination) | Scaffold |
| `@bloque/ui` | shadcn/ui componentes base | Scaffold |
| `@bloque/api-client` | Cliente HTTP con interceptors | Scaffold |

## Quick Start

### Prerequisitos

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Node.js 20+
- [pnpm](https://pnpm.io/) (Node package manager)

### Instalacion

```bash
# Clonar
git clone https://github.com/abelardodiaz/web25-991-bloques-reciclables.git
cd web25-991-bloques-reciclables

# Python
uv sync --all-packages

# TypeScript
pnpm install
```

### Correr tests

```bash
# Python
uv run pytest

# TypeScript
pnpm run build
```

### Ejemplo rapido

```bash
cd examples/api-simple
uv run uvicorn main:app --reload
# Visitar http://localhost:8000/health
```

## Usar en tu proyecto

```bash
# Agregar bloque-core a tu proyecto
uv add bloque-core

# Agregar bloque-auth
uv add bloque-auth
```

```python
from fastapi import FastAPI
from bloque_core.middleware import RequestIDMiddleware, TimingMiddleware
from bloque_core.health import health_router
from bloque_core.logging import setup_logging

app = FastAPI()
setup_logging()
app.add_middleware(TimingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.include_router(health_router)
```

## Recetas

Combinaciones de bloques para casos de uso comunes:

- [API Simple](docs/recetas/api-simple.md) - FastAPI basico con core
- [SaaS Multitenant](docs/recetas/saas-multitenant.md) - API con RLS + auth
- [MVP sin Login](docs/recetas/mvp-sin-login.md) - Prototipo rapido
- [Bot WhatsApp](docs/recetas/bot-whatsapp.md) - Webhook + channels

## Arquitectura

```
web25-991-bloques-reciclables/
  packages/
    python/               # uv workspaces
      bloque-core/        # Middleware, schemas, logging, health
      bloque-auth/        # JWT, RBAC, brute force, credentials
      bloque-multitenant/ # PostgreSQL RLS transparente
    typescript/           # pnpm + Turborepo
      bloque-ui/          # Componentes UI (futuro)
      bloque-api-client/  # Cliente HTTP (futuro)
      bloque-types/       # TypeScript types base
  templates/              # Copier templates composables
  examples/               # Proyectos ejemplo
  docs/                   # Documentacion
```

## Principios

1. **Cada bloque es independiente.** Sin dependencias circulares.
2. **bloque-core es el unico obligatorio.** Todo lo demas es opcional.
3. **Tests en cada bloque.** Cada package tiene sus propios tests.
4. **Sin secrets.** Repo publico. Nunca hardcodear credenciales.
5. **Documentar con ejemplos.** Cada bloque tiene README con ejemplo.

## Contributing

1. Fork el repo
2. Crea un branch (`git checkout -b feat/mi-feature`)
3. Commit con conventional commits (`feat:`, `fix:`, `docs:`)
4. Push y abre un PR

## Herramientas

| Herramienta | Proposito |
|------------|----------|
| [uv](https://docs.astral.sh/uv/) | Python package management + workspaces |
| [pnpm](https://pnpm.io/) | Node package management + workspaces |
| [Turborepo](https://turbo.build/) | Build orchestration TS |
| [Ruff](https://docs.astral.sh/ruff/) | Python linter + formatter |
| [pytest](https://pytest.org/) | Python tests |

## License

[MIT](LICENSE)
