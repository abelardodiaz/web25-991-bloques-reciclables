# Receta: SaaS Multitenant

> Con bloque-core + bloque-auth + bloque-multitenant construyes un SaaS completo.

---

## Bloques necesarios

```bash
uv add bloque-core bloque-auth bloque-multitenant
```

## Que obtienes

- API FastAPI con middleware stack completo (request ID, timing, auth)
- JWT RS256 con tenant_id y roles en payload
- RBAC granular con dependencias FastAPI
- Proteccion brute force en login
- PostgreSQL RLS transparente (el developer nunca escribe codigo multitenant)
- TenantCredential para almacenar API keys por tenant (Fernet AES-256)
- Health checks y logging estructurado

## Setup rapido

```python
from fastapi import FastAPI
from bloque_core.middleware import RequestIDMiddleware, TimingMiddleware
from bloque_core.health import health_router
from bloque_core.logging import setup_logging
from bloque_auth.jwt import JWTManager
from bloque_auth.rbac import require_permission
from bloque_multitenant.rls import RLSMiddleware
from bloque_multitenant.context import TenantContext

app = FastAPI(title="Mi SaaS Multitenant")
setup_logging()

# Middleware stack (orden importa)
app.add_middleware(RLSMiddleware)         # 3. Inyecta SET LOCAL
app.add_middleware(JWTManager.middleware)  # 2. Extrae tenant_id del JWT
app.add_middleware(RequestIDMiddleware)    # 1. Genera request ID
app.add_middleware(TimingMiddleware)

app.include_router(health_router)

@app.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_permission("users:read"))
):
    # RLS filtra automaticamente por tenant
    return await db.execute(select(User))
```

## Base de datos

```sql
-- Ejecutar una vez al crear la BD
-- bloque-multitenant provee script de setup

-- 1. Habilitar RLS en cada tabla
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 2. Crear policy
CREATE POLICY tenant_isolation ON users
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- 3. Default deny si no hay tenant
ALTER TABLE users FORCE ROW LEVEL SECURITY;
```

## Frontend (opcional)

```bash
pnpm add @bloque/ui @bloque/api-client @bloque/auth-react
```

Agrega login, tenant selector, y dashboard basico.

## Siguiente paso

Agregar mas bloques segun necesidad:
- `bloque-redis` para cache y event streaming
- `bloque-notifications` para emails y push
- `bloque-billing` para pagos con Stripe
