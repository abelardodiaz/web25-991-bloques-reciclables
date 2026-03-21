# Receta: SaaS Multitenant

> Con ulfblk-core + ulfblk-auth + ulfblk-db + ulfblk-multitenant construyes un SaaS completo.

---

## Bloques necesarios

```bash
uv add ulfblk-core ulfblk-auth ulfblk-db ulfblk-multitenant aiosqlite
```

## Que obtienes

- API FastAPI con `create_app()` factory
- JWT RS256 con tenant_id y roles en payload
- RBAC granular con `require_permissions()` y `require_roles()`
- Proteccion brute force en login
- SQLAlchemy async con mixins composables (TimestampMixin, SoftDeleteMixin)
- Tenant context via contextvars (async-safe)
- PostgreSQL RLS transparente (opcional, para produccion)
- SQLite zero-config para desarrollo

## Ejemplo completo

Ver `examples/saas-multitenant/` para el ejemplo funcional con:
- `models.py` - User y Order con mixins composables
- `database.py` - Engine + session factory via ulfblk-db
- `seed.py` - Datos demo para 2 tenants
- `main.py` - App completa con login, RBAC, tenant filtering

## Setup rapido

```python
from ulfblk_core import create_app, get_logger, setup_logging
from ulfblk_auth.jwt import JWTManager
from ulfblk_auth.rbac.permissions import configure, get_current_user, require_permissions
from ulfblk_db import Base, TimestampMixin, create_async_engine, create_session_factory, get_db_session, DatabaseSettings
from ulfblk_multitenant.context import set_current_tenant
from fastapi import Depends
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession

# Modelos (TU defines tus modelos, no los bloques)
class User(Base, TimestampMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    tenant_id = Column(String, nullable=False)

# Setup
setup_logging()
jwt_manager = JWTManager(private_key=PRIVATE_PEM, public_key=PUBLIC_PEM)
configure(jwt_manager)

settings = DatabaseSettings(database_url="sqlite+aiosqlite:///./app.db")
engine = create_async_engine(settings)
SessionLocal = create_session_factory(engine)
db_dep = get_db_session(SessionLocal)

app = create_app(service_name="mi-saas", version="0.1.0")

@app.get("/users")
async def list_users(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(db_dep),
):
    set_current_tenant(tenant_id=user.tenant_id)
    result = await db.execute(
        select(User).where(User.tenant_id == user.tenant_id)
    )
    return {"users": [{"id": u.id, "email": u.email} for u in result.scalars()]}
```

## Con PostgreSQL RLS (produccion)

```python
from ulfblk_multitenant.rls import apply_rls, generate_rls_sql

# 1. Generar SQL para RLS (ejecutar en migracion)
sql = generate_rls_sql("users", tenant_column="tenant_id")

# 2. Configurar engine con event listener
apply_rls(engine)

# 3. Agregar middleware de tenant
from ulfblk_multitenant.rls import TenantMiddleware
app.add_middleware(TenantMiddleware)
# Ahora las queries se filtran automaticamente por tenant
```

## Frontend (opcional)

```bash
pnpm add @ulfblk/ui @ulfblk/api-client @ulfblk/auth-react
```

## Siguiente paso

- `ulfblk-redis` para cache y event streaming
- `ulfblk-notifications` para emails y push
- `ulfblk-billing` para pagos con Stripe
