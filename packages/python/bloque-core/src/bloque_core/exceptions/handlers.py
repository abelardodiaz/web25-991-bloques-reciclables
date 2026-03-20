"""Exception handlers that return standardized ErrorResponse."""

import logging
import traceback

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with standardized error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "code": f"HTTP_{exc.status_code}",
            "errors": None,
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors with field-level detail."""
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "code": "VALIDATION_ERROR",
            "errors": exc.errors(),
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions without leaking internals."""
    logger.error(
        "Unhandled exception: path=%s method=%s\n%s",
        request.url.path,
        request.method,
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "code": "INTERNAL_ERROR",
            "errors": None,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers on the app."""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
