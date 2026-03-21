"""AvailabilityMixin: composable SQLAlchemy mixin for recurring availability."""

from datetime import time
from typing import Optional

from sqlalchemy import Boolean, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column


class AvailabilityMixin:
    """Adds recurring availability columns for weekly schedules.

    Defines day_of_week (0=Monday, 6=Sunday), start_time, end_time,
    resource_id, and is_active columns.

    Example::

        class DoctorAvailability(Base, AvailabilityMixin):
            __tablename__ = "doctor_availability"
            id = Column(Integer, primary_key=True)
            doctor_id = Column(Integer, ForeignKey("doctors.id"))
    """

    day_of_week: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )
    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )
    resource_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default=None,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
