"""Health check router."""

from fastapi import APIRouter

from ..schemas.base import HealthResponse

health_router = APIRouter(tags=["health"])


@health_router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Basic health check endpoint."""
    return HealthResponse.healthy(service="api", version="0.1.0")
