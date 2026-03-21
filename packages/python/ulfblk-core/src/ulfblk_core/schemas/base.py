"""Base schemas for standardized API responses."""

from datetime import UTC, datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base for all schemas."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class PaginatedResponse(BaseSchema, Generic[T]):
    """Standardized paginated response."""

    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int = 1,
        page_size: int = 20,
    ) -> "PaginatedResponse[T]":
        pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )


class ErrorResponse(BaseSchema):
    """Standardized error response."""

    detail: str
    code: str | None = None
    errors: list[dict[str, Any]] | None = None


class SuccessResponse(BaseSchema):
    """Simple success response."""

    message: str
    data: dict[str, Any] | None = None


class HealthResponse(BaseSchema):
    """Health check response."""

    status: str
    service: str
    version: str
    timestamp: datetime
    checks: dict[str, bool] | None = None

    @classmethod
    def healthy(cls, service: str, version: str) -> "HealthResponse":
        return cls(
            status="healthy",
            service=service,
            version=version,
            timestamp=datetime.now(UTC),
        )

    @classmethod
    def unhealthy(
        cls, service: str, version: str, checks: dict[str, bool]
    ) -> "HealthResponse":
        return cls(
            status="unhealthy",
            service=service,
            version=version,
            timestamp=datetime.now(UTC),
            checks=checks,
        )
