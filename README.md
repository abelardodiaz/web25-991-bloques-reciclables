# ulfblk

Composable Python + TypeScript packages for building SaaS applications. Install what you need, skip what you don't.

```bash
uv add ulfblk-core ulfblk-db ulfblk-auth
```

## Getting Started

```python
from ulfblk_core import create_app
from ulfblk_db import Base, TimestampMixin, create_async_engine, create_session_factory

# 1. Create your app (includes middleware, health check, error handling)
app = create_app(service_name="my-api", version="0.1.0")

# 2. Define your models with composable mixins
class User(Base, TimestampMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)

# 3. Run
# uv run uvicorn main:app --reload
# -> http://localhost:8000/docs
```

## Packages

### Python (PyPI)

| Package | Description |
|---------|-------------|
| `ulfblk-core` | App factory, middleware, schemas, health checks, logging |
| `ulfblk-db` | SQLAlchemy async engine, session factory, composable mixins, Alembic migrations |
| `ulfblk-auth` | JWT RS256, RBAC, brute force protection, credential encryption |
| `ulfblk-multitenant` | PostgreSQL RLS transparent multitenancy via contextvars |
| `ulfblk-testing` | Pytest plugin with auto-registered fixtures (JWT, DB, HTTP client) |
| `ulfblk-redis` | Cache, streams, consumer groups, tenant-aware key prefixing |
| `ulfblk-gateway` | Rate limiting, reverse proxy, circuit breaker |
| `ulfblk-channels` | WhatsApp, Telegram, Email webhook handlers |
| `ulfblk-billing` | Stripe integration (customers, subscriptions, checkout, webhooks) |
| `ulfblk-notifications` | Email + push + templates |
| `ulfblk-automation` | Rule engine + condition evaluator |
| `ulfblk-ai-rag` | ChromaDB + LLM gateway (DeepSeek, OpenAI, Ollama) |
| `ulfblk-ci-github` | GitHub Actions workflow generator |
| `ulfblk-ci-gitlab` | GitLab CI pipeline generator |
| `ulfblk-docker-dev` | Docker Compose for development |
| `ulfblk-docker-prod` | Docker Compose for production + nginx |

### TypeScript (npm)

| Package | Description |
|---------|-------------|
| `@ulfblk/types` | TypeScript types (auth, pagination, entities, tenants) |
| `@ulfblk/ui` | Tailwind CSS preset + cn() utility + design tokens |
| `@ulfblk/api-client` | HTTP client with interceptors + token management |
| `@ulfblk/auth-react` | React hooks + providers + guards for auth |
| `@ulfblk/dashboard` | Dashboard layout components (sidebar, header, data tables) |

## Examples

| Example | What it demonstrates |
|---------|---------------------|
| [SaaS Multitenant](examples/saas-multitenant/) | 4 bloques with real SQLAlchemy DB, JWT auth, tenant isolation |
| [MVP sin Login](examples/mvp-sin-login/) | Full-stack Next.js + FastAPI, zero auth |
| [API Simple](examples/api-simple/) | Minimal API with just ulfblk-core |

## Recipes

Step-by-step guides for common use cases:

- [API Simple](docs/recetas/api-simple.md) - FastAPI with health check in 10 lines
- [SaaS Multitenant](docs/recetas/saas-multitenant.md) - JWT + RBAC + DB + RLS
- [MVP sin Login](docs/recetas/mvp-sin-login.md) - Quick prototype, no auth
- [Bot WhatsApp](docs/recetas/bot-whatsapp.md) - Webhook + RAG chatbot

## How It Works

ulfblk packages export infrastructure, not business logic. You compose them:

```python
from ulfblk_db import Base, TimestampMixin, SoftDeleteMixin

class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    tenant_id = Column(String, nullable=False)
    orders = relationship("Order", back_populates="user")
```

Relationships, business rules, and data models are yours. Bloques provide the plumbing.

## Development

```bash
git clone https://github.com/abelardodiaz/web25-991-bloques-reciclables.git
cd web25-991-bloques-reciclables

# Python
uv sync --all-packages
uv run pytest

# TypeScript
pnpm install
pnpm run build
```

## Comparison

See [docs/COMPARATIVA.md](docs/COMPARATIVA.md) for an honest comparison vs Django, Laravel, SaaS Pegasus, ShipFast, Supabase, and create-t3-app.

## License

[MIT](LICENSE)
