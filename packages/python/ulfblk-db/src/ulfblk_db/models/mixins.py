"""Composable SQLAlchemy mixins for common model patterns."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Adds created_at and updated_at columns with auto-defaults.

    Example::

        class Order(Base, TimestampMixin):
            __tablename__ = "orders"
            id = Column(Integer, primary_key=True)
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Adds soft delete support via deleted_at column.

    Example::

        class Document(Base, SoftDeleteMixin):
            __tablename__ = "documents"
            id = Column(Integer, primary_key=True)

        doc = Document()
        doc.soft_delete()
        assert doc.is_deleted
        doc.restore()
        assert not doc.is_deleted
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    @property
    def is_deleted(self) -> bool:
        """Return True if this record has been soft-deleted."""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Mark this record as deleted by setting deleted_at to now."""
        self.deleted_at = datetime.now()

    def restore(self) -> None:
        """Restore a soft-deleted record by clearing deleted_at."""
        self.deleted_at = None
