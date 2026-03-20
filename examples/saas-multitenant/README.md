# SaaS Multitenant Example

Full SaaS API example demonstrating all three Python bloques working together:
- **bloque-core**: Middleware, schemas, structured logging, health check
- **bloque-auth**: JWT RS256, RBAC, brute force protection
- **bloque-multitenant**: Tenant context isolation (simulated RLS)

## Run

```bash
cd examples/saas-multitenant
uv run uvicorn main:app --reload
```

Open http://localhost:8000/docs for the interactive Swagger UI.

## Demo Flow

### 1. Login as ACME admin

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@acme.com", "password": "admin123"}'
```

Save the `access_token` from the response.

### 2. Get current user info

```bash
curl http://localhost:8000/me \
  -H "Authorization: Bearer <TOKEN>"
```

### 3. List orders (filtered by tenant)

```bash
curl http://localhost:8000/orders \
  -H "Authorization: Bearer <TOKEN>"
```

ACME admin sees only ACME orders. Globex admin sees only Globex orders.

### 4. Admin-only endpoint

```bash
curl http://localhost:8000/admin/users \
  -H "Authorization: Bearer <TOKEN>"
```

### 5. Permission-protected endpoint

```bash
curl -X DELETE http://localhost:8000/admin/users/user-2 \
  -H "Authorization: Bearer <TOKEN>"
```

Only users with `users:delete` permission can access this.

### 6. Brute force protection

Try logging in with wrong password 5 times - the account gets locked for 15 minutes.

## Test Users

| Email | Password | Tenant | Roles | Key Permissions |
|-------|----------|--------|-------|-----------------|
| admin@acme.com | admin123 | acme | admin | all |
| user@acme.com | user123 | acme | user | orders:read, orders:write |
| admin@globex.com | admin123 | globex | admin | users:read, users:write, orders:read |

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /auth/login | - | Login with email/password |
| GET | /me | Bearer | Current user info |
| GET | /orders | orders:read | List tenant orders |
| GET | /admin/users | admin role | List tenant users |
| DELETE | /admin/users/{id} | users:delete | Delete user |
| GET | /health | - | Health check |

## With Real PostgreSQL RLS

For production use with actual PostgreSQL Row-Level Security:

```python
from sqlalchemy.ext.asyncio import create_async_engine
from bloque_multitenant.rls import TenantMiddleware, apply_rls, generate_rls_sql

# 1. Generate RLS SQL for your tables
sql = generate_rls_sql("orders", tenant_column="tenant_id")
# Execute this SQL in your migration

# 2. Configure SQLAlchemy
engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/mydb")
apply_rls(engine)

# 3. Add middleware
app.add_middleware(TenantMiddleware)
# Tenant context is now automatic - all queries filtered by RLS
```
