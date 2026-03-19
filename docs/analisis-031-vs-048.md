# Analisis y Reciclaje: Domus SaaS (031) vs CRM Multi-tenant (048)

> Guia para crear un ecosistema SaaS reciclable combinando lo mejor de ambos proyectos.
> Validado por debates multi-IA (Gemini + DeepSeek) con web search - API 900 tickets 740, 741, 742, 743.
> Fecha: 2026-03-19

---

## Resumen Ejecutivo

| Dimension | Domus SaaS (031) | CRM Multi-tenant (048) | Ganador |
|-----------|-------------------|------------------------|---------|
| Server | server003 | server005 | - |
| Path | `/home/ubuntu/web25-031-domus-saas/` | `/home/ubuntu/projects/web25-048-crm/` | - |
| Version | 0.12.0 | 0.16.0 | - |
| Backend | Django+DRF (7) + FastAPI (2) | FastAPI puro (11 svc) | **048** |
| Frontend | Next.js 16, flat, sin shadcn | Next.js 16, monorepo pnpm, Radix UI | **048** |
| Multitenant | Row-level (tenant_id en BD unica) | Database-per-tenant (BD por slug) | **048** |
| Auth | Django SimpleJWT + RBAC | JWT RS256 + RBAC granular | Empate |
| Shared code | 3 archivos | Package completo (23+ archivos) | **048** |
| Comunicacion inter-svc | Nada formal | HTTP + Redis Streams | **048** |
| DevOps | Docker 13 containers | Docker + PM2 dual mode | Empate |

**048 CRM gana en casi todo.** 031 Domus tiene 3 componentes unicos valiosos.

---

## Componentes Reciclables

### De 048 (CRM) - Base principal

| Componente | Ruta SSH | Descripcion |
|-----------|----------|-------------|
| `crm_shared` package | `server005:/home/ubuntu/projects/web25-048-crm/shared/python/crm_shared/` | DatabaseManager async, JWT, Redis, middleware, schemas, logging (23+ archivos) |
| API Gateway | `server005:.../services/api-gateway/src/main.py` | Auth middleware, rate limit, proxy, request ID |
| Auth service | `server005:.../services/auth-service/` | JWT RS256, RBAC, roles, permisos |
| Frontend monorepo | `server005:.../frontend/packages/` | @crm/ui (20 componentes), @crm/api-client, @crm/types |
| Redis Streams | `server005:.../shared/python/crm_shared/redis/` | StreamPublisher, StreamConsumer con consumer groups |
| Rule Engine | `server005:.../services/automation-service/src/engine/` | Condition evaluator, action executor |
| AI/RAG service | `server005:.../services/ai-service/` | DeepSeek, Ollama, ChromaDB, clasificacion |
| Channels/WhatsApp | `server005:.../services/channels-service/` | Webhook processing, message routing |
| Notifications | `server005:.../services/notification-service/` | Templates, preferencias, email/push |

### De 031 (Domus) - Componentes unicos

| Componente | Ruta SSH | Descripcion |
|-----------|----------|-------------|
| TenantCredential | `server003:/home/ubuntu/web25-031-domus-saas/backend/services/auth/core/models/credential.py` | Fernet AES-256 encryption para API keys por tenant (WhatsApp, Stripe, SMTP, etc). NO existe en 048. |
| Brute force protection | `server003:.../backend/services/auth/core/models/user.py` | failed_login_attempts, locked_until, last_login_ip |
| Activity logging | `server003:.../backend/services/auth/core/models/` | ActivityLog model para auditoria |
| SoftDeleteMixin | `server003:.../backend/shared/models/base.py` | is_deleted, deleted_at (048 no lo tiene) |
| Docker prod + nginx | `server003:.../docker-compose.prod.yml` + `docker/nginx.conf` | Setup de produccion containerizado |

---

## Arquitectura Golden Path (Validada por Debates)

### Estrategia: Templates + Packages (Hibrida)

Los templates dan estructura (scaffolding), los packages dan logica reutilizable que evoluciona independientemente.

### Capa 1: Packages Reutilizables

#### Backend - `saas_shared` (uv workspace + PyPI dual-mode)

Basado en `crm_shared` de 048, ampliado con componentes de 031.

```
saas_shared/
  pyproject.toml          # uv workspace root
  uv.lock                 # Lockfile unificado
  packages/
    saas_core/            # OBLIGATORIO - minimo absoluto
      auth/               # JWT RS256 + RBAC dependencies (048)
      database/           # DatabaseManager async + RLS middleware (048 + NUEVO)
      middleware/         # RequestID, Timing, Auth (048)
      schemas/            # PaginatedResponse[T], Health, Error (048)
      logging/            # structlog + request ID (048)
    saas_auth/            # Auth completo
      brute_force.py      # failed_attempts + locked_until (031)
      credentials.py      # TenantCredential + Fernet AES-256 (031 portado)
      activity_log.py     # Auditoria (031 portado)
    saas_billing/         # Plugin opcional
    saas_ai/              # Plugin opcional (ChromaDB, LLM gateway)
```

**Consumo dual:**
- Greenfield: `uv workspace` con dependencias locales
- Brownfield: `uv add saas-shared-core` desde PyPI privado

#### Frontend - `@saas/*` (pnpm workspaces)

Basado en packages de 048, migrado a shadcn/ui.

```
packages/
  @saas/ui/              # shadcn/ui (upgrade de Radix UI de 048)
  @saas/api-client/      # Axios + interceptors + token management (048)
  @saas/types/           # TypeScript types base (048)
  @saas/auth/            # React hooks + providers (NUEVO, extraido de 048)
```

### Capa 2: Templates de Estructura (Copier composable)

```
copier-saas-ecosystem/
  copier.yaml                    # Config raiz con preguntas
  template-base/                 # Turborepo + pnpm + uv workspace
  template-backend-fastapi/      # API + saas_shared conectado
  template-frontend-nextjs/      # Dashboard + tenant selector + login
  features/                      # Plugins opcionales
    auth-clerk/
    billing-stripe/
    chromadb-ai/
    redis-streams/
    monitoring/
```

**Flujo greenfield:**
```bash
copier copy gh:org/copier-saas-ecosystem my-saas
cd my-saas && copier copy template-backend-fastapi .
copier copy template-frontend-nextjs .
copier copy features/chromadb-ai .      # opcional
```

**Flujo brownfield (migracion):**
```bash
cd existing-project
copier copy gh:org/copier-saas-ecosystem/template-backend-fastapi .
# Copier hace merge inteligente respetando codigo existente
```

### Capa 3: Patron Multitenant

**PostgreSQL RLS transparente** (no row-level ORM ni database-per-tenant forzado).

```python
# El developer NUNCA escribe codigo multitenant manualmente.
# saas_core/database/rls_middleware.py hace todo automaticamente:

from contextvars import ContextVar
from sqlalchemy import event

_tenant_context: ContextVar[str] = ContextVar("tenant_id")

# 1. Middleware FastAPI extrae tenant_id del JWT
@app.middleware("http")
async def tenant_middleware(request, call_next):
    tenant_id = extract_from_jwt(request)
    token = _tenant_context.set(tenant_id)
    response = await call_next(request)
    _tenant_context.reset(token)
    return response

# 2. SQLAlchemy event listener inyecta SET LOCAL automaticamente
@event.listens_for(engine.sync_engine, "connect")
def set_tenant(dbapi_connection, connection_record):
    tenant_id = _tenant_context.get(None)
    if tenant_id:
        cursor = dbapi_connection.cursor()
        cursor.execute(f"SET LOCAL app.current_tenant = '{tenant_id}'")
        cursor.close()

# 3. El developer solo escribe logica de negocio normal
async def list_users(db: AsyncSession = Depends(get_db)):
    return await db.execute(select(User))  # Auto-filtrado por RLS
```

**Fail-safe**: si contextvar vacio, PostgreSQL deniega acceso (RLS default deny).

---

## Herramientas 2025 Validadas por Web Search

| Herramienta | Proposito | Estado 2025 | URL |
|------------|----------|-------------|-----|
| **uv (Astral)** | Gestion dependencias Python | Workspaces nativos, reemplaza Poetry/Pipenv | docs.astral.sh/uv |
| **Copier** | Living templates | Merge inteligente con `copier update` | copier.readthedocs.io |
| **Turborepo** | Monorepo JS/TS | Golden stack con pnpm, cache remota | turbo.build |
| **PostgreSQL RLS** | Multitenant seguro | Sin impacto rendimiento con buenos indices | supabase.com/docs |
| **ChromaDB** | Vector DB multitenant | Tenants y Databases jerarquicas nativas | docs.trychroma.com |
| **next-forge** | Boilerplate Next.js | Referencia (no fork directo, muy acoplado a BaaS) | next-forge.com |
| **Redis Streams** | Event-driven | Opcion pragmatica si ya usas Redis | redis.io/docs |

---

## MVP (Minimo Viable del Ecosistema)

4 componentes para valor dia 1:

### 1. `saas_shared-core` (Paquete Python)
- Middleware RLS automatico (contextvars + SQLAlchemy events)
- Auth JWT RS256 con tenant_id en payload
- TenantContext propagation
- Pydantic Settings base

### 2. Template Base Copier
- Estructura Turborepo + pnpm + uv workspace
- Docker Compose para PostgreSQL + Redis
- CI/CD basico (GitHub Actions)
- Pre-commit hooks + Ruff linter

### 3. Boilerplate Backend FastAPI
- API Gateway con middleware stack
- Auth service (login, refresh, RBAC)
- Un CRUD de ejemplo multitenant
- Health checks

### 4. Boilerplate Frontend Next.js
- Login + tenant selector
- Dashboard basico
- API client generado desde OpenAPI
- shadcn/ui + Tailwind

**Metrica de exito:** Un developer puede crear y deployar un servicio multitenant en < 1 hora.

---

## Roadmap Sugerido

| Fase | Duracion | Entregable |
|------|----------|-----------|
| 1. Core | 2-3 semanas | saas_shared-core + template base Copier |
| 2. Templates | 2-3 semanas | Backend FastAPI + Frontend Next.js templates |
| 3. Plugins | Por demanda | ChromaDB AI, Stripe billing, Redis Streams |
| 4. Migracion | Por proyecto | Strangler Fig para 031 y/o 048 |

---

## Debates API 900 (Referencia)

| Ticket | Tipo | Providers | Tema |
|--------|------|-----------|------|
| 740 | Debate | gemini, deepseek | Evaluacion estrategia hibrida (10 turnos) |
| 741 | Web search | gemini | PostgreSQL RLS, uv, Turborepo, ChromaDB, Copier, next-forge, Backstage |
| 742 | Web search | deepseek | FastAPI boilerplates, Python monorepo, Redis Streams vs NATS |
| 743 | Debate enriquecido | gemini, deepseek | Arquitectura final con hallazgos web (10 turnos, consenso total) |

---

## Notas

- Este template sirve IGUAL para proyectos nuevos (greenfield) como para migrar existentes (brownfield)
- Strangler Fig y evolucion de TenantCredential son opciones para migracion, NO requisitos del template
- TenantCredential con Fernet es suficiente para v1; evolucionar a Vault es futuro opcional
- next-forge es referencia/inspiracion, no base directa (demasiado acoplado a Supabase/Clerk)
