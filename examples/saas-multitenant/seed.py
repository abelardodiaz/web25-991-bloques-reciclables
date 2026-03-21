"""Seed demo data into the database.

Idempotent: skips if users already exist.
Passwords are stored in plain text - this is a demo, not production code.
"""

from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from models import Order, User


async def seed_data(session_factory: async_sessionmaker) -> None:
    """Insert demo users and orders if the database is empty."""
    async with session_factory() as session:
        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none() is not None:
            return  # Already seeded

        users = [
            User(
                email="admin@acme.com",
                name="Alice Admin",
                password="admin123",
                tenant_id="acme",
                roles_json=json.dumps(["admin"]),
                permissions_json=json.dumps([
                    "users:read", "users:write", "users:delete",
                    "orders:read", "orders:write",
                ]),
            ),
            User(
                email="user@acme.com",
                name="Bob User",
                password="user123",
                tenant_id="acme",
                roles_json=json.dumps(["user"]),
                permissions_json=json.dumps(["orders:read", "orders:write"]),
            ),
            User(
                email="admin@globex.com",
                name="Carol Admin",
                password="admin123",
                tenant_id="globex",
                roles_json=json.dumps(["admin"]),
                permissions_json=json.dumps([
                    "users:read", "users:write", "orders:read",
                ]),
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
