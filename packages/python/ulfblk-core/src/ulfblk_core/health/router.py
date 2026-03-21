"""Health check router."""

from fastapi import APIRouter

from ..schemas.base import HealthResponse


def create_health_router(
    service_name: str = "api",
    version: str = "0.1.0",
) -> APIRouter:
    """Create a health check router with configurable service info."""
    router = APIRouter(tags=["health"])

    @router.get("/health", response_model=HealthResponse)
    async def health_check() -> HealthResponse:
        """Basic health check endpoint."""
        return HealthResponse.healthy(service=service_name, version=version)

    return router


# Backwards-compatible default instance
health_router = create_health_router()
