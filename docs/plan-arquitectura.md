# Plan: Ecosistema SaaS Reciclable desde 031 + 048

## Contexto

Tenemos dos proyectos SaaS multitenant maduros (Domus 031 y CRM 048). Queremos extraer lo mejor de ambos para crear un ecosistema reciclable que sirva tanto para proyectos nuevos (greenfield) como para migrar existentes (brownfield). Validado por 2 debates multi-IA + 2 web searches (API 900 tickets 740-743).

---

## Quien Gana Que

| Dimension | Ganador | Por que |
|-----------|---------|---------|
| Backend stack | **048** | FastAPI puro uniforme, shared package completo |
| Frontend | **048** | Monorepo pnpm, Radix UI, React Query |
| Multitenant | **Ninguno** | Ambos patrones limitados. RLS nativo de PostgreSQL es mejor (hallazgo web) |
| Auth/Seguridad | **Combinar** | 048 tiene mejor RBAC, 031 tiene brute force + TenantCredential + audit log |
| Comunicacion | **048** | Redis Streams + ServiceClient con request ID |
| DevOps | **Combinar** | PM2 de 048 para dev, Docker+nginx de 031 para prod |

---

## Arquitectura Final (Consenso Gemini + DeepSeek)

### Multitenant: PostgreSQL RLS transparente (NUEVO - ni 031 ni 048 lo usan)

Ni row-level ORM (031) ni database-per-tenant (048). **PostgreSQL RLS nativo** con inyeccion automatica:

```python
# El developer NUNCA escribe codigo multitenant. Todo automatico:
# 1. Middleware FastAPI extrae tenant_id del JWT -> contextvar
# 2. SQLAlchemy event listener inyecta SET LOCAL app.current_tenant
# 3. PostgreSQL RLS filtra automaticamente. Si contextvar vacio, deniega acceso.
```

Supabase demostro que RLS no impacta rendimiento con buenos indices. Para tenants Enterprise que requieran aislamiento total, database-per-tenant como upgrade.

### Backend: uv workspace + PyPI dual-mode

```
saas_shared/                     # uv workspace root
  pyproject.toml + uv.lock
  packages/
    saas_core/                   # OBLIGATORIO
      database/rls_middleware.py # SET LOCAL via contextvars + SQLAlchemy events
      auth/jwt.py               # JWT RS256 con roles+perms en payload (048)
      auth/brute_force.py       # failed_attempts + locked_until (031)
      credentials/fernet.py     # TenantCredential AES-256 (031 portado)
      middleware/                # RequestID, Timing, Auth (048)
      schemas/                  # PaginatedResponse[T], Health, Error (048)
      logging/                  # structlog + request ID (048)
    saas_auth/                   # Plugin: auth completo
    saas_billing/                # Plugin: Stripe
    saas_ai/                     # Plugin: ChromaDB con client.set_tenant() nativo
```

- **Greenfield**: uv workspaces con dependencias locales
- **Brownfield**: `uv add saas-shared-core` desde PyPI privado
- **Herramienta**: uv de Astral (reemplaza Poetry/Pipenv, workspaces nativos con lockfile unificado)

### Frontend: Turborepo + pnpm custom (inspirado en next-forge, NO fork)

```
frontend/
  turbo.json
  pnpm-workspace.yaml
  packages/
    @saas/ui/              # shadcn/ui (migrado de Radix UI de 048)
    @saas/api-client/      # Generado desde OpenAPI de FastAPI (no manual)
    @saas/types/           # TypeScript types base
    @saas/auth/            # React hooks + providers
  apps/
    dashboard/             # Next.js 16 + React 19 + Tailwind
```

next-forge es referencia de estructura, no base directa (demasiado acoplado a Supabase/Clerk).

### Templates: Copier composable (NO Cookiecutter)

```
copier-saas-ecosystem/
  copier.yaml                    # Preguntas interactivas
  template-base/                 # Turborepo + pnpm + uv workspace + CI/CD
  template-backend-fastapi/      # API + saas_shared + CRUD ejemplo
  template-frontend-nextjs/      # Login + tenant selector + dashboard
  features/                      # Plugins opcionales (via preguntas Copier)
    chromadb-ai/
    billing-stripe/
    redis-streams/
```

- Greenfield: `copier copy gh:org/copier-saas-ecosystem my-saas`
- Brownfield: `copier copy template-backend-fastapi existing-project/` (merge inteligente)
- Updates: `copier update` propaga cambios del template respetando codigo custom

---

## Componentes a Reciclar (con rutas SSH)

### De 048 CRM (base principal)
- `server005:.../shared/python/crm_shared/` -> base de saas_shared (23+ archivos)
- `server005:.../services/api-gateway/src/main.py` -> template gateway
- `server005:.../services/auth-service/` -> template auth
- `server005:.../frontend/packages/` -> base de @saas/* (ui, api-client, types)
- `server005:.../shared/python/crm_shared/redis/` -> Redis Streams pattern

### De 031 Domus (componentes unicos)
- `server003:.../backend/services/auth/core/models/credential.py` -> TenantCredential + Fernet
- `server003:.../backend/services/auth/core/models/user.py` -> brute force protection
- `server003:.../backend/shared/models/base.py` -> SoftDeleteMixin
- `server003:.../docker-compose.prod.yml` + `docker/nginx.conf` -> template Docker prod

---

## MVP (4 componentes, valor dia 1)

1. **saas_shared-core**: RLS middleware + Auth JWT + TenantContext
2. **Template Base Copier**: Turborepo + pnpm + uv workspace + Docker Compose
3. **Boilerplate Backend**: FastAPI con CRUD multitenant funcional
4. **Boilerplate Frontend**: Next.js con login + tenant selector + dashboard

Metrica: developer crea servicio multitenant en < 1 hora.

---

## Herramientas 2025 (validadas por web search)

| Herramienta | Reemplaza | URL |
|------------|-----------|-----|
| uv (Astral) | Poetry, Pipenv | docs.astral.sh/uv |
| Copier | Cookiecutter | copier.readthedocs.io |
| Turborepo | pnpm scripts manuales | turbo.build |
| PostgreSQL RLS | Filtrado ORM (tenant_id) | supabase.com/docs |
| ChromaDB tenants | Hacks con metadata | docs.trychroma.com |

---

## Entregable de esta Sesion

### Archivos ya creados:
1. `docs/saas-reciclaje-031-048.md` - Guia completa con rutas SSH, arquitectura, MVP
2. `CLAUDE.md` - Actualizado con referencia
3. `PROJECT.yaml` - v0.30.0

### Pendiente:
- Commit + push a ambos remotes

### Verificacion:
1. Spot check 3-4 rutas SSH de archivos clave
2. Commit + push github + origin
