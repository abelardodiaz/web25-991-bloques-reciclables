"""AppointmentMixin: composable SQLAlchemy mixin for appointment models."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class AppointmentMixin:
    """Adds appointment columns and status transition methods.

    Provides scheduled_at, duration_minutes, status, resource_id, and notes
    columns. Includes convenience methods for common status transitions.

    Example::

        class Appointment(Base, TimestampMixin, AppointmentMixin):
            __tablename__ = "appointments"
            id = Column(Integer, primary_key=True)
            patient_id = Column(Integer, ForeignKey("patients.id"))
    """

    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=30,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
    )
    resource_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        default=None,
    )
    notes: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        default=None,
    )

    def cancel(self) -> None:
        """Transition appointment status to cancelled."""
        self.status = "cancelled"

    def confirm(self) -> None:
        """Transition appointment status to confirmed."""
        self.status = "confirmed"

    def complete(self) -> None:
        """Transition appointment status to completed."""
        self.status = "completed"

    def mark_no_show(self) -> None:
        """Transition appointment status to no_show."""
        self.status = "no_show"
