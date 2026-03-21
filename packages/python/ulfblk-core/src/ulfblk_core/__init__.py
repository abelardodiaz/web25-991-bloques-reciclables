"""ulfblk-core: Core utilities for building web APIs."""

__version__ = "0.1.0"

from .app import create_app
from .config.settings import BloqueSettings
from .exceptions.handlers import register_exception_handlers
from .health.router import create_health_router, health_router
from .logging.setup import get_logger, setup_logging
from .middleware.request_id import RequestIDMiddleware
from .middleware.timing import TimingMiddleware
from .schemas.base import (
    BaseSchema,
    ErrorResponse,
    HealthResponse,
    PaginatedResponse,
    SuccessResponse,
)

__all__ = [
    "BaseSchema",
    "BloqueSettings",
    "ErrorResponse",
    "HealthResponse",
    "PaginatedResponse",
    "RequestIDMiddleware",
    "SuccessResponse",
    "TimingMiddleware",
    "create_app",
    "create_health_router",
    "get_logger",
    "health_router",
    "register_exception_handlers",
    "setup_logging",
]
