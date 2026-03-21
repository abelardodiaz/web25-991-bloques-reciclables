"""Seed demo data into the database.

Idempotent: skips if users already exist.
Passwords are hashed with SHA-256 + salt.
"""

from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from models import Order, User


def _create_user(email: str, name: str, password: str, tenant_id: str,
                 roles: list[str], permissions: list[str]) -> User:
    """Create a User with hashed password."""
    user = User(
        email=email,
        name=name,
        password_hash="",
        tenant_id=tenant_id,
        roles_json=json.dumps(roles),
        permissions_json=json.dumps(permissions),
    )
    user.set_password(password)
    return user


async def seed_data(session_factory: async_sessionmaker) -> None:
    """Insert demo users and orders if the database is empty."""
    async with session_factory() as session:
        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none() is not None:
            return  # Already seeded

        users = [
            _create_user(
                "admin@acme.com", "Alice Admin", "admin123", "acme",
                ["admin"],
                ["users:read", "users:write", "users:delete", "orders:read", "orders:write"],
            ),
            _create_user(
                "user@acme.com", "Bob User", "user123", "acme",
                ["user"],
                ["orders:read", "orders:write"],
            ),
            _create_user(
                "admin@globex.com", "Carol Admin", "admin123", "globex",
                ["admin"],
                ["users:read", "users:write", "orders:read"],
            ),
        ]
        session.add_all(users)
        await session.flush()

        orders = [
            Order(product="Widget A", amount=150.00, tenant_id="acme", user_id=users[0].id),
            Order(product="Widget B", amount=299.99, tenant_id="acme", user_id=users[0].id),
            Order(product="Gadget X", amount=499.00, tenant_id="globex", user_id=users[2].id),
        ]
        session.add_all(orders)
        await session.commit()
