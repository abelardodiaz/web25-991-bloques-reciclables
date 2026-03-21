# Bloques Compatibility Matrix

> Last tested: 2026-03-21
> Test suite: `tests/integration/`
> Run with: `uv run pytest tests/integration/ -v`

## Tested Combinations

| ulfblk-core | ulfblk-db | ulfblk-auth | ulfblk-multitenant | ulfblk-testing | Status |
|-------------|-----------|-------------|--------------------|-----------------------------------------|--------|
| 0.1.0       | 0.1.0     | 0.1.0       | 0.1.0              | 0.1.0          | PASS   |

## Shared Dependencies

All bloques target Python >= 3.11 and share these foundational dependencies:

| Dependency         | Required By             | Version Range |
|--------------------|-------------------------|---------------|
| fastapi            | core, testing           | >= 0.115.0    |
| pydantic           | core                    | >= 2.0        |
| pydantic-settings  | core                    | >= 2.0        |
| sqlalchemy[asyncio]| db, multitenant         | >= 2.0        |
| pyjwt[crypto]      | auth, testing[auth]     | >= 2.8        |
| cryptography       | auth, testing[auth]     | >= 42.0       |

## Dependency Graph

```
ulfblk-core (standalone, no bloque deps)
  |
  +-- ulfblk-db (depends on ulfblk-core)
  |
  +-- ulfblk-auth (depends on ulfblk-core)
  |
  +-- ulfblk-multitenant (depends on ulfblk-core)
  |
  +-- ulfblk-testing (optional deps on ulfblk-auth, ulfblk-db)
```

No circular dependencies. Each bloque depends only on ulfblk-core.

## How Composability Works

Bloques do NOT export concrete models. They export:

- **ulfblk-core**: App factory, middleware, settings, schemas, health checks
- **ulfblk-db**: `Base`, mixins (`TimestampMixin`, `SoftDeleteMixin`), engine/session factories
- **ulfblk-auth**: `JWTManager`, RBAC dependencies (`require_permissions`, `require_roles`)
- **ulfblk-multitenant**: `TenantContext`, `TenantMiddleware`, RLS SQL generation

The developer defines their own models in their application:

```python
from ulfblk_db import Base, TimestampMixin, SoftDeleteMixin
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    tenant_id = Column(String, nullable=False)
    orders = relationship("Order", back_populates="user")

class Order(Base, TimestampMixin):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tenant_id = Column(String, nullable=False)
    user = relationship("User", back_populates="orders")
```

Relationships between models are defined by the application, not by bloques.
This is by design: bloques provide infrastructure, not business logic.

## Updating This Matrix

When a bloque version changes:

1. Update the version in its `pyproject.toml`
2. Run `uv run pytest tests/integration/ -v`
3. If all pass, update the table above
4. If failures occur, document incompatibilities
