"""Application factory for FastAPI apps with Bloque defaults."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from .config.settings import BloqueSettings
from .exceptions.handlers import register_exception_handlers
from .health.router import create_health_router
from .logging.setup import setup_logging
from .middleware.request_id import RequestIDMiddleware
from .middleware.timing import TimingMiddleware


def create_app(
    service_name: str = "api",
    version: str = "0.1.0",
    settings: BloqueSettings | None = None,
    **fastapi_kwargs: Any,
) -> FastAPI:
    """Create a fully configured FastAPI application.

    Args:
        service_name: Name for the service (used in health, title).
        version: Service version string.
        settings: Optional BloqueSettings instance. If provided, its values
            take precedence over service_name/version args.
        **fastapi_kwargs: Extra keyword arguments passed to FastAPI().
    """
    if settings is not None:
        service_name = settings.service_name
        version = settings.version

    effective_log_level = settings.log_level if settings else "INFO"
    effective_json_format = settings.log_json_format if settings else False

    setup_logging(
        level=effective_log_level,
        json_format=effective_json_format,
        service_name=service_name,
    )

    fastapi_kwargs.setdefault("title", service_name)
    fastapi_kwargs.setdefault("version", version)

    app = FastAPI(**fastapi_kwargs)

    # Middleware order: RequestID first (outermost), then Timing
    # Starlette applies middleware in reverse add order, so add Timing first
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    app.include_router(create_health_router(service_name=service_name, version=version))

    register_exception_handlers(app)

    return app
