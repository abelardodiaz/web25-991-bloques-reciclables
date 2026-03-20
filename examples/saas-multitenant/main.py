"""SaaS Multitenant API example.

Demonstrates:
- bloque-core: middleware, schemas, logging, health
- bloque-auth: JWT RS256, RBAC, brute force protection
- bloque-multitenant: tenant context via contextvars

Run with:
    cd examples/saas-multitenant
    uv run uvicorn main:app --reload

Note: This example uses in-memory data. For real PostgreSQL RLS,
see the setup instructions in the README.
"""

from bloque_auth.brute_force import BruteForceProtection, LoginAttemptState
from bloque_auth.jwt import JWTManager
from bloque_auth.rbac import (
    configure,
    get_current_user,
    require_permissions,
    require_roles,
)
from bloque_core.health import health_router
from bloque_core.logging import get_logger, setup_logging
from bloque_core.middleware import RequestIDMiddleware, TimingMiddleware
from bloque_core.schemas import PaginatedResponse
from bloque_multitenant.context import get_current_tenant, set_current_tenant
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel

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

# ---------------------------------------------------------------------------
# In-memory data (simulates database)
# ---------------------------------------------------------------------------
USERS = {
    "admin@acme.com": {
        "user_id": "user-1",
        "password": "admin123",
        "tenant_id": "acme",
        "roles": ["admin"],
        "permissions": ["users:read", "users:write", "users:delete", "orders:read", "orders:write"],
    },
    "user@acme.com": {
        "user_id": "user-2",
        "password": "user123",
        "tenant_id": "acme",
        "roles": ["user"],
        "permissions": ["orders:read", "orders:write"],
    },
    "admin@globex.com": {
        "user_id": "user-3",
        "password": "admin123",
        "tenant_id": "globex",
        "roles": ["admin"],
        "permissions": ["users:read", "users:write", "orders:read"],
    },
}

ORDERS = {
    "acme": [
        {"id": "ord-1", "product": "Widget A", "amount": 150.00, "tenant_id": "acme"},
        {"id": "ord-2", "product": "Widget B", "amount": 299.99, "tenant_id": "acme"},
    ],
    "globex": [
        {"id": "ord-3", "product": "Gadget X", "amount": 499.00, "tenant_id": "globex"},
    ],
}

LOGIN_STATES: dict[str, LoginAttemptState] = {}

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="SaaS Multitenant Example",
    description="Demonstrates bloque-core + bloque-auth + bloque-multitenant",
    version="0.1.0",
)

app.add_middleware(TimingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.include_router(health_router)


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


class OrderOut(BaseModel):
    id: str
    product: str
    amount: float
    tenant_id: str


# ---------------------------------------------------------------------------
# Auth endpoints
# ---------------------------------------------------------------------------
@app.post("/auth/login", response_model=LoginResponse)
async def login(body: LoginRequest):
    """Login with email/password. Returns JWT tokens."""
    # Check brute force
    state = LOGIN_STATES.get(body.email, LoginAttemptState())
    if brute_force.is_locked(state):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Account temporarily locked due to too many failed attempts",
        )

    user = USERS.get(body.email)
    if not user or user["password"] != body.password:
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
        user_id=user["user_id"],
        tenant_id=user["tenant_id"],
        roles=user["roles"],
        permissions=user["permissions"],
    )
    refresh_token = jwt_manager.create_refresh_token(
        user_id=user["user_id"],
        tenant_id=user["tenant_id"],
    )

    logger.info("login.success", user_id=user["user_id"], tenant=user["tenant_id"])
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
async def list_orders(user=Depends(require_permissions("orders:read"))):
    """List orders for the current tenant. Simulates RLS filtering."""
    # Set tenant context (in production, TenantMiddleware does this)
    set_current_tenant(tenant_id=user.tenant_id)
    tenant = get_current_tenant()

    # Simulate RLS: filter by tenant
    tenant_orders = ORDERS.get(tenant.tenant_id, [])
    items = [OrderOut(**o) for o in tenant_orders]

    logger.info("orders.listed", tenant=tenant.tenant_id, count=len(items))
    return PaginatedResponse.create(items=items, total=len(items))


@app.get("/admin/users")
async def admin_users(user=Depends(require_roles("admin"))):
    """Admin-only: list all users in the tenant."""
    tenant_users = [
        {"email": email, "user_id": u["user_id"], "roles": u["roles"]}
        for email, u in USERS.items()
        if u["tenant_id"] == user.tenant_id
    ]
    return {"users": tenant_users, "tenant": user.tenant_id}


@app.delete("/admin/users/{user_id}")
async def delete_user(user_id: str, user=Depends(require_permissions("users:delete"))):
    """Requires users:delete permission."""
    logger.info("user.deleted", target_user=user_id, by=user.user_id, tenant=user.tenant_id)
    return {"message": f"User {user_id} deleted (simulated)", "tenant": user.tenant_id}
