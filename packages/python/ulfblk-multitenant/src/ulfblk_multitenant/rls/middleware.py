"""FastAPI middleware for automatic tenant context injection.

The developer NEVER writes multitenant code manually:
1. This middleware extracts tenant_id from JWT -> contextvar
2. SQLAlchemy event listener injects SET LOCAL app.current_tenant
3. PostgreSQL RLS filters automatically
"""

from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from ..context.tenant import clear_current_tenant, set_current_tenant


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware that extracts tenant_id from the request and sets it in the context.

    The tenant_id is extracted using a configurable callable. By default,
    it looks for tenant_id in the request state (set by auth middleware).

    Args:
        app: ASGI application
        tenant_extractor: Callable that extracts tenant_id from a Request.
            Receives the Request, returns Optional[str].
    """

    def __init__(self, app, tenant_extractor: Callable | None = None):
        super().__init__(app)
        self.tenant_extractor = tenant_extractor or self._default_extractor

    @staticmethod
    def _default_extractor(request: Request) -> str | None:
        """Default: get tenant_id from request.state (set by auth middleware)."""
        return getattr(request.state, "tenant_id", None)

    async def dispatch(self, request: Request, call_next) -> Response:
        tenant_id = self.tenant_extractor(request)

        if tenant_id:
            set_current_tenant(tenant_id=tenant_id)

        try:
            response = await call_next(request)
        finally:
            clear_current_tenant()

        return response
