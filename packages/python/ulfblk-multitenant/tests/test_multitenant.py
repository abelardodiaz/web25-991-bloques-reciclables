"""Tests for ulfblk-multitenant context and RLS utilities."""


from ulfblk_multitenant.context import (
    TenantContext,
    get_current_tenant,
    set_current_tenant,
)
from ulfblk_multitenant.context.tenant import clear_current_tenant
from ulfblk_multitenant.rls.setup import generate_rls_sql


class TestTenantContext:
    def test_set_and_get_tenant(self):
        ctx = set_current_tenant(tenant_id="t-001", tenant_slug="acme")
        assert ctx.tenant_id == "t-001"
        assert ctx.tenant_slug == "acme"

        current = get_current_tenant()
        assert current is not None
        assert current.tenant_id == "t-001"

    def test_clear_tenant(self):
        set_current_tenant(tenant_id="t-001")
        clear_current_tenant()
        assert get_current_tenant() is None

    def test_default_is_none(self):
        clear_current_tenant()
        assert get_current_tenant() is None

    def test_tenant_context_immutable(self):
        ctx = TenantContext(tenant_id="t-001", tenant_slug="acme")
        assert ctx.tenant_id == "t-001"
        assert ctx.tenant_slug == "acme"
        assert ctx.tenant_name is None


class TestRLSSetup:
    def test_generate_rls_sql_default_column(self):
        sql = generate_rls_sql("users")
        assert "ALTER TABLE users ENABLE ROW LEVEL SECURITY" in sql
        assert "tenant_id" in sql
        assert "app.current_tenant" in sql

    def test_generate_rls_sql_custom_column(self):
        sql = generate_rls_sql("orders", tenant_column="org_id")
        assert "org_id" in sql
        assert "tenant_id" not in sql

    def test_generate_rls_sql_force_rls(self):
        sql = generate_rls_sql("products")
        assert "FORCE ROW LEVEL SECURITY" in sql

    def test_generate_rls_sql_policy_name(self):
        sql = generate_rls_sql("invoices")
        assert "tenant_isolation" in sql
