"""Tests that bloque-multitenant tenant context works with bloque-db models."""

import asyncio

from sqlalchemy import select

from bloque_multitenant.context import get_current_tenant, set_current_tenant
from bloque_multitenant.rls import generate_rls_sql

from .conftest import Order, User


class TestMultitenantWithDatabase:
    async def test_filter_users_by_tenant(self, db_session, sample_data):
        """Application-level tenant filtering returns only matching users."""
        set_current_tenant(tenant_id="acme")
        tenant = get_current_tenant()

        result = await db_session.execute(
            select(User).where(User.tenant_id == tenant.tenant_id)
        )
        users = result.scalars().all()
        assert len(users) == 1
        assert users[0].email == "admin@acme.com"

    async def test_filter_orders_by_tenant(self, db_session, sample_data):
        """Tenant filtering on orders returns only that tenant's orders."""
        set_current_tenant(tenant_id="acme")
        tenant = get_current_tenant()

        result = await db_session.execute(
            select(Order).where(Order.tenant_id == tenant.tenant_id)
        )
        orders = result.scalars().all()
        assert len(orders) == 2
        assert all(o.tenant_id == "acme" for o in orders)

    def test_rls_sql_generation_for_app_tables(self):
        """generate_rls_sql produces correct SQL for app-defined tables."""
        sql = generate_rls_sql("users")
        assert "ALTER TABLE users ENABLE ROW LEVEL SECURITY" in sql
        assert "tenant_id" in sql
        assert "current_setting('app.current_tenant'" in sql

        sql_orders = generate_rls_sql("orders", tenant_column="tenant_id")
        assert "ALTER TABLE orders ENABLE ROW LEVEL SECURITY" in sql_orders

    async def test_tenant_context_async_isolation(self):
        """Concurrent tasks have isolated tenant contexts (contextvars)."""
        results = {}

        async def set_and_read(name: str):
            set_current_tenant(tenant_id=name)
            await asyncio.sleep(0.01)
            tenant = get_current_tenant()
            results[name] = tenant.tenant_id

        await asyncio.gather(
            set_and_read("acme"),
            set_and_read("globex"),
        )
        assert results["acme"] == "acme"
        assert results["globex"] == "globex"
