"""Shared fixtures for integration tests.

These fixtures prove real-world composability by defining application
models that use mixins from multiple bloques, then wiring up the full
stack: engine, sessions, JWT auth, RBAC, and FastAPI app.

Models are defined HERE (the developer's app), NOT inside any bloque.
This is the entire point: bloques export infrastructure, the dev
defines their own models.
"""

from __future__ import annotations

import pytest
from fastapi import Depends, FastAPI
from sqlalchemy import Column, Float, ForeignKey, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, relationship

from bloque_auth.jwt import JWTManager
from bloque_auth.rbac.permissions import configure as configure_rbac
from bloque_auth.rbac.permissions import get_current_user, require_permissions
from bloque_db import Base, SoftDeleteMixin, TimestampMixin, get_db_session
from bloque_testing.auth import create_jwt_manager, create_test_token
from bloque_testing.db import create_tables, create_test_engine, create_test_session_factory, drop_tables


# ---------------------------------------------------------------------------
# Application models (defined by the developer, not by bloques)
# ---------------------------------------------------------------------------


class User(Base, TimestampMixin, SoftDeleteMixin):
    """User model composing Base + TimestampMixin + SoftDeleteMixin."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    tenant_id = Column(String(100), nullable=False, index=True)

    orders: Mapped[list[Order]] = relationship("Order", back_populates="user")


class Order(Base, TimestampMixin):
    """Order model with FK to User. Proves cross-model relationships work."""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    tenant_id = Column(String(100), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user: Mapped[User] = relationship("User", back_populates="orders")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def engine():
    """SQLite in-memory async engine."""
    return create_test_engine()


@pytest.fixture
async def tables(engine):
    """Create all tables before test, drop after."""
    await create_tables(engine, Base)
    yield
    await drop_tables(engine, Base)


@pytest.fixture
def session_factory(engine):
    """Session factory bound to in-memory engine."""
    return create_test_session_factory(engine)


@pytest.fixture
async def db_session(session_factory, tables):
    """Yields a single async session per test."""
    async with session_factory() as session:
        yield session


@pytest.fixture
def jwt_manager():
    """JWTManager configured for testing, registered with RBAC."""
    manager = create_jwt_manager()
    configure_rbac(manager)
    return manager


@pytest.fixture
async def sample_data(db_session):
    """Insert sample users and orders for 2 tenants."""
    user_acme = User(email="admin@acme.com", name="Alice", tenant_id="acme")
    user_globex = User(email="admin@globex.com", name="Bob", tenant_id="globex")
    db_session.add_all([user_acme, user_globex])
    await db_session.flush()

    order1 = Order(product="Widget A", amount=150.0, tenant_id="acme", user_id=user_acme.id)
    order2 = Order(product="Widget B", amount=300.0, tenant_id="acme", user_id=user_acme.id)
    order3 = Order(product="Gadget X", amount=499.0, tenant_id="globex", user_id=user_globex.id)
    db_session.add_all([order1, order2, order3])
    await db_session.commit()

    return {"acme_user": user_acme, "globex_user": user_globex}


@pytest.fixture
async def integration_app(engine, tables, session_factory, jwt_manager):
    """Full-stack FastAPI app with auth + DB endpoints."""
    app = FastAPI(title="Integration Test")

    db_dep = get_db_session(session_factory)

    # Seed data
    async with session_factory() as session:
        u1 = User(email="admin@acme.com", name="Alice", tenant_id="acme")
        u2 = User(email="admin@globex.com", name="Bob", tenant_id="globex")
        session.add_all([u1, u2])
        await session.flush()
        o1 = Order(product="Widget A", amount=150.0, tenant_id="acme", user_id=u1.id)
        o2 = Order(product="Gadget X", amount=499.0, tenant_id="globex", user_id=u2.id)
        session.add_all([o1, o2])
        await session.commit()

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    @app.get("/api/users")
    async def list_users(
        user=Depends(get_current_user),
        db: AsyncSession = Depends(db_dep),
    ):
        result = await db.execute(
            select(User).where(User.tenant_id == user.tenant_id)
        )
        users = result.scalars().all()
        return {
            "users": [
                {"id": u.id, "email": u.email, "tenant_id": u.tenant_id}
                for u in users
            ]
        }

    @app.post("/api/users")
    async def create_user_endpoint(
        user=Depends(get_current_user),
        db: AsyncSession = Depends(db_dep),
    ):
        new_user = User(
            email=f"new-{user.user_id}@test.com",
            name="New User",
            tenant_id=user.tenant_id,
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return {"id": new_user.id, "email": new_user.email}

    @app.get("/api/orders")
    async def list_orders(
        user=Depends(require_permissions("orders:read")),
        db: AsyncSession = Depends(db_dep),
    ):
        result = await db.execute(
            select(Order).where(Order.tenant_id == user.tenant_id)
        )
        orders = result.scalars().all()
        return {
            "orders": [
                {"id": o.id, "product": o.product, "tenant_id": o.tenant_id}
                for o in orders
            ]
        }

    return app
