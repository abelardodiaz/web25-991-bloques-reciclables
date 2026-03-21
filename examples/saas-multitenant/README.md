# SaaS Multitenant Example

Full SaaS API example demonstrating 4 Python bloques working together with a real database:

- **bloque-core**: App factory (`create_app`), middleware, schemas, health check
- **bloque-auth**: JWT RS256, RBAC, brute force protection
- **bloque-db**: SQLAlchemy models with composable mixins, async engine, session factory
- **bloque-multitenant**: Tenant context isolation via contextvars

## How It Works

This example shows how a developer composes bloques into a real application:

1. **Models** (`models.py`): `User(Base, TimestampMixin, SoftDeleteMixin)` and `Order(Base, TimestampMixin)` with FK relationships
2. **Database** (`database.py`): Engine + session factory via `bloque-db`, zero config with SQLite
3. **Seed data** (`seed.py`): Demo users and orders for 2 tenants (Acme, Globex)
4. **App** (`main.py`): FastAPI with JWT auth, RBAC, tenant-filtered DB queries, soft delete

## Run

```bash
cd examples/saas-multitenant
uv run uvicorn main:app --reload
```

Uses SQLite by default (creates `demo.db` in current directory). For PostgreSQL:

```bash
export BLOQUE_DATABASE_URL=postgresql+asyncpg://user:pass@localhost/mydb
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

### 3. List orders (filtered by tenant from JWT)

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

### 5. Soft-delete a user (requires users:delete permission)

```bash
curl -X DELETE http://localhost:8000/admin/users/2 \
  -H "Authorization: Bearer <TOKEN>"
```

The user is soft-deleted (deleted_at set, not removed from DB).

### 6. Brute force protection

Try logging in with wrong password 5 times - the account gets locked for 15 minutes.

## Test Users

| Email | Password | Tenant | Roles | Key Permissions |
|-------|----------|--------|-------|-----------------|
| admin@acme.com | admin123 | acme | admin | all |
| user@acme.com | user123 | acme | user | orders:read, orders:write |
| admin@globex.com | admin123 | globex | admin | users:read, users:write, orders:read |

> Passwords stored in plain text - this is a demo, not production code.

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /auth/login | - | Login with email/password |
| GET | /me | Bearer | Current user info from JWT |
| GET | /orders | orders:read | List tenant orders from DB |
| GET | /admin/users | admin role | List active tenant users from DB |
| DELETE | /admin/users/{id} | users:delete | Soft-delete user |
| GET | /health | - | Health check |

## With PostgreSQL RLS

For production with actual Row-Level Security:

```python
from bloque_multitenant.rls import apply_rls, generate_rls_sql

# 1. Generate and execute RLS SQL in your migration
sql = generate_rls_sql("orders", tenant_column="tenant_id")

# 2. Configure SQLAlchemy engine with RLS event listener
apply_rls(engine)

# 3. Add TenantMiddleware - tenant context is now automatic
app.add_middleware(TenantMiddleware)
```
