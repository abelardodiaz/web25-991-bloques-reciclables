"""Tenant context using contextvars for async-safe propagation."""

from contextvars import ContextVar
from dataclasses import dataclass


@dataclass
class TenantContext:
    """Immutable tenant context for the current request."""

    tenant_id: str
    tenant_slug: str | None = None
    tenant_name: str | None = None


_tenant_var: ContextVar[TenantContext | None] = ContextVar("tenant_context", default=None)


def get_current_tenant() -> TenantContext | None:
    """Get the current tenant context."""
    return _tenant_var.get()


def set_current_tenant(
    tenant_id: str,
    tenant_slug: str | None = None,
    tenant_name: str | None = None,
) -> TenantContext:
    """
    Set the current tenant context.
    Returns the created TenantContext.
    """
    ctx = TenantContext(
        tenant_id=tenant_id,
        tenant_slug=tenant_slug,
        tenant_name=tenant_name,
    )
    _tenant_var.set(ctx)
    return ctx


def clear_current_tenant() -> None:
    """Clear the current tenant context."""
    _tenant_var.set(None)
