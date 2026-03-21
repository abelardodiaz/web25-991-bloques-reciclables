# ulfblk-multitenant

PostgreSQL Row-Level Security (RLS) transparent multitenancy for FastAPI + SQLAlchemy. The developer never writes tenant filtering code manually.

Part of [Bloques Reciclables](https://github.com/abelardodiaz/web25-991-bloques-reciclables) - an open source ecosystem of reusable code blocks.

## Installation

```bash
uv add ulfblk-multitenant
# or
pip install ulfblk-multitenant
```

## How It Works

1. **TenantMiddleware** extracts `tenant_id` from the request (e.g., from JWT via auth middleware)
2. **TenantContext** stores it in a `contextvar` (async-safe)
3. **SQLAlchemy event listener** injects `SET LOCAL app.current_tenant` on each transaction
4. **PostgreSQL RLS policies** filter rows automatically

The developer writes normal queries - RLS handles isolation transparently.

## Quick Start

### 1. Generate RLS SQL

```python
from ulfblk_multitenant.rls import generate_rls_sql

# Generate and execute in your migration
sql = generate_rls_sql("orders", tenant_column="tenant_id")
# Enables RLS, creates tenant_isolation policy
```

### 2. Configure SQLAlchemy

```python
from sqlalchemy.ext.asyncio import create_async_engine
from ulfblk_multitenant.rls import apply_rls

engine = create_async_engine("postgresql+asyncpg://...")
apply_rls(engine)  # registers the event listener
```

### 3. Add Middleware

```python
from fastapi import FastAPI
from ulfblk_multitenant.rls import TenantMiddleware

app = FastAPI()

# Default: reads tenant_id from request.state.tenant_id
app.add_middleware(TenantMiddleware)

# Or custom extractor:
app.add_middleware(
    TenantMiddleware,
    tenant_extractor=lambda req: req.headers.get("X-Tenant-ID"),
)
```

### 4. Use TenantContext Directly

```python
from ulfblk_multitenant.context import get_current_tenant, set_current_tenant, clear_current_tenant

# Set manually (useful in background tasks, scripts)
ctx = set_current_tenant(
    tenant_id="acme-123",
    tenant_slug="acme",
    tenant_name="ACME Corp",
)

# Read current tenant
tenant = get_current_tenant()
if tenant:
    print(f"Current tenant: {tenant.tenant_id}")

# Clear
clear_current_tenant()
```

## With ulfblk-auth

The typical setup combines `ulfblk-auth` JWT middleware with `ulfblk-multitenant`:

```python
from fastapi import FastAPI
from ulfblk_core.middleware import RequestIDMiddleware
from ulfblk_multitenant.rls import TenantMiddleware, apply_rls

app = FastAPI()

# Middleware stack (order matters - last added runs first)
app.add_middleware(TenantMiddleware)  # 3. Set tenant context from JWT
# ... auth middleware sets request.state.tenant_id ...
app.add_middleware(RequestIDMiddleware)  # 1. Set request ID

# SQLAlchemy RLS
apply_rls(engine)

# Now all queries are automatically filtered by tenant
@app.get("/orders")
async def list_orders(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Order))
    return result.scalars().all()  # only current tenant's orders
```

## Dependencies

- [ulfblk-core](https://github.com/abelardodiaz/web25-991-bloques-reciclables/tree/main/packages/python/ulfblk-core)
- SQLAlchemy 2.0+ (async)
- asyncpg

## Requirements

- Python 3.11+
- PostgreSQL 14+ (RLS support)

## License

[MIT](https://github.com/abelardodiaz/web25-991-bloques-reciclables/blob/main/LICENSE)
