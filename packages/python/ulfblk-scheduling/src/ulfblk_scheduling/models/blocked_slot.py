"""BlockedSlotMixin: composable SQLAlchemy mixin for blocked time slots."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column


class BlockedSlotMixin:
    """Adds blocked time slot columns for unavailable periods.

    Defines start_at, end_at, resource_id, and reason columns for
    marking time ranges as unavailable (holidays, breaks, etc).

    Example::

        class BlockedSlot(Base, BlockedSlotMixin):
            __tablename__ = "blocked_slots"
            id = Column(Integer, primary_key=True)
    """

    start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    end_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    resource_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default=None,
    )
    reason: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        default=None,
    )
