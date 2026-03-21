"""SaaS Multitenant API - Real Database Example.

Demonstrates 4 bloques working together with a real database:
- bloque-core: App factory, middleware, schemas, health check
- bloque-auth: JWT RS256, RBAC, brute force protection
- bloque-db: SQLAlchemy models with composable mixins, async engine
- bloque-multitenant: Tenant context via contextvars

Uses SQLite by default (zero config). For PostgreSQL:
    export BLOQUE_DATABASE_URL=postgresql+asyncpg://user:pass@localhost/mydb

Run with:
    cd examples/saas-multitenant
    uv run uvicorn main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from bloque_auth.brute_force import BruteForceProtection, LoginAttemptState
from bloque_auth.jwt import JWTManager
from bloque_auth.rbac import (
    configure,
    get_current_user,
    require_permissions,
    require_roles,
)
from bloque_core import create_app, get_logger, setup_logging
from bloque_core.schemas import PaginatedResponse
from bloque_multitenant.context import get_current_tenant, set_current_tenant
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import SessionLocal, db_dep, init_db
from models import Order, User
from seed import seed_data

# ---------------------------------------------------------------------------
# RSA key pair (generated at startup for demo - in production use env vars)
# ---------------------------------------------------------------------------
_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
PRIVATE_KEY_PEM = _private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
).decode()
PUBLIC_KEY_PEM = _private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
).decode()

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
setup_logging(level="INFO")
logger = get_logger(__name__)

jwt_manager = JWTManager(
    private_key=PRIVATE_KEY_PEM,
    public_key=PUBLIC_KEY_PEM,
    access_token_expire_minutes=60,
)
configure(jwt_manager)

brute_force = BruteForceProtection(max_attempts=5, lockout_minutes=15)
LOGIN_STATES: dict[str, LoginAttemptState] = {}


# ---------------------------------------------------------------------------
# Lifespan: init DB + seed data
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app):
    await init_db()
    await seed_data(SessionLocal)
    logger.info("database.ready", msg="Tables created and demo data seeded")
    yield


# ---------------------------------------------------------------------------
# App (using create_app from bloque-core)
# ---------------------------------------------------------------------------
app = create_app(
    service_name="saas-multitenant",
    version="0.1.0",
    title="SaaS Multitenant Example",
    description="Demonstrates bloque-core + bloque-auth + bloque-db + bloque-multitenant",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    tenant_id: str
    roles: list[str]


class OrderOut(BaseModel):
    id: int
    product: str
    amount: float
    tenant_id: str


# ---------------------------------------------------------------------------
# Auth endpoints
# ---------------------------------------------------------------------------
@app.post("/auth/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(db_dep)):
    """Login with email/password. Returns JWT tokens."""
    # Check brute force
    state = LOGIN_STATES.get(body.email, LoginAttemptState())
    if brute_force.is_locked(state):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Account temporarily locked due to too many failed attempts",
        )

    # Query user from database
    result = await db.execute(
        select(User).where(User.email == body.email, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()

    if not user or user.password != body.password:
        state = brute_force.record_failed_attempt(state)
        LOGIN_STATES[body.email] = state
        logger.warning("login.failed", email=body.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Success
    state = brute_force.record_successful_login(state)
    LOGIN_STATES[body.email] = state

    access_token = jwt_manager.create_access_token(
        user_id=str(user.id),
        tenant_id=user.tenant_id,
        roles=user.get_roles(),
        permissions=user.get_permissions(),
    )
    refresh_token = jwt_manager.create_refresh_token(
        user_id=str(user.id),
        tenant_id=user.tenant_id,
    )

    logger.info("login.success", user_id=user.id, tenant=user.tenant_id)
    return LoginResponse(access_token=access_token, refresh_token=refresh_token)


# ---------------------------------------------------------------------------
# Protected endpoints
# ---------------------------------------------------------------------------
@app.get("/me")
async def me(user=Depends(get_current_user)):
    """Get current user info from JWT."""
    return {
        "user_id": user.user_id,
        "tenant_id": user.tenant_id,
        "roles": user.roles,
        "permissions": user.permissions,
    }


@app.get("/orders", response_model=PaginatedResponse[OrderOut])
async def list_orders(
    user=Depends(require_permissions("orders:read")),
    db: AsyncSession = Depends(db_dep),
):
    """List orders for the current tenant."""
    set_current_tenant(tenant_id=user.tenant_id)

    result = await db.execute(
        select(Order).where(Order.tenant_id == user.tenant_id)
    )
    orders = result.scalars().all()
    items = [
        OrderOut(id=o.id, product=o.product, amount=o.amount, tenant_id=o.tenant_id)
        for o in orders
    ]

    logger.info("orders.listed", tenant=user.tenant_id, count=len(items))
    return PaginatedResponse.create(items=items, total=len(items))


@app.get("/admin/users")
async def admin_users(
    user=Depends(require_roles("admin")),
    db: AsyncSession = Depends(db_dep),
):
    """Admin-only: list all active users in the tenant."""
    result = await db.execute(
        select(User).where(
            User.tenant_id == user.tenant_id,
            User.deleted_at.is_(None),
        )
    )
    users = result.scalars().all()
    return {
        "users": [
            UserOut(
                id=u.id, email=u.email, name=u.name,
                tenant_id=u.tenant_id, roles=u.get_roles(),
            ).model_dump()
            for u in users
        ],
        "tenant": user.tenant_id,
    }


@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    user=Depends(require_permissions("users:delete")),
    db: AsyncSession = Depends(db_dep),
):
    """Soft-delete a user (requires users:delete permission)."""
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.tenant_id == user.tenant_id,
            User.deleted_at.is_(None),
        )
    )
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    target.soft_delete()
    await db.commit()

    logger.info("user.soft_deleted", target_user=user_id, by=user.user_id, tenant=user.tenant_id)
    return {"message": f"User {user_id} soft-deleted", "tenant": user.tenant_id}
