"""PostgreSQL RLS setup utilities.

Generates SQL for RLS policies and configures SQLAlchemy to inject
SET LOCAL app.current_tenant automatically on each connection.
"""


from sqlalchemy import event, text
from sqlalchemy.engine import Engine

from ..context.tenant import get_current_tenant


def generate_rls_sql(table_name: str, tenant_column: str = "tenant_id") -> str:
    """
    Generate SQL statements to enable RLS on a table.

    Returns SQL that:
    1. Enables RLS on the table
    2. Creates a policy that filters by app.current_tenant
    3. Default deny if no tenant set

    Args:
        table_name: Name of the table to protect
        tenant_column: Column that holds the tenant identifier

    Returns:
        SQL string to execute
    """
    return f"""
-- Enable RLS on {table_name}
ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;
ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;

-- Policy: only show rows matching current tenant
CREATE POLICY tenant_isolation ON {table_name}
    USING ({tenant_column}::text = current_setting('app.current_tenant', true))
    WITH CHECK ({tenant_column}::text = current_setting('app.current_tenant', true));
"""


def apply_rls(engine: Engine) -> None:
    """
    Register SQLAlchemy event listener that injects SET LOCAL app.current_tenant.

    Call this once at application startup with your SQLAlchemy engine.
    After this, every database connection will automatically have the
    tenant context set from the contextvar.

    Args:
        engine: SQLAlchemy engine (sync or async - for async, pass engine.sync_engine)
    """
    sync_engine = getattr(engine, "sync_engine", engine)

    @event.listens_for(sync_engine, "after_begin")
    def _set_tenant_on_begin(session, transaction, connection):
        tenant_ctx = get_current_tenant()
        if tenant_ctx and tenant_ctx.tenant_id:
            connection.execute(
                text("SET LOCAL app.current_tenant = :tenant_id"),
                {"tenant_id": tenant_ctx.tenant_id},
            )
