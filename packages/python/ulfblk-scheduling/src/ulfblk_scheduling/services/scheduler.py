"""Scheduler service: async appointment lifecycle management."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.settings import SchedulingSettings
from ..exceptions import ConflictError
from ..schemas.appointment import AppointmentCreate


async def create_appointment(
    session: AsyncSession,
    model_class: type[Any],
    data: AppointmentCreate,
    settings: SchedulingSettings | None = None,
) -> Any:
    """Create a new appointment with concurrency-safe conflict checking.

    Uses SELECT ... FOR UPDATE to prevent double-booking in concurrent
    scenarios. Validates against existing appointments for the same
    resource and time range.

    Args:
        session: Active async database session.
        model_class: The SQLAlchemy model class for appointments.
        data: Appointment creation data.
        settings: Optional scheduling settings for defaults.

    Returns:
        The newly created appointment instance.

    Raises:
        ConflictError: If the requested time conflicts with an existing appointment.

    Example::

        appointment = await create_appointment(
            session=db_session,
            model_class=Appointment,
            data=AppointmentCreate(scheduled_at=dt, duration_minutes=30),
        )
    """
    if settings is None:
        settings = SchedulingSettings()

    duration = data.duration_minutes or settings.default_duration_minutes
    end_time = data.scheduled_at + timedelta(minutes=duration)

    # Query overlapping appointments with row-level lock for concurrency safety
    stmt = select(model_class).where(
        model_class.status != "cancelled",
        model_class.scheduled_at < end_time,
    )

    # Add resource filter if provided
    if data.resource_id is not None and hasattr(model_class, "resource_id"):
        stmt = stmt.where(model_class.resource_id == data.resource_id)

    stmt = stmt.with_for_update()
    result = await session.execute(stmt)
    existing = result.scalars().all()

    # Check for overlapping appointments
    overlapping = [
        appt for appt in existing
        if appt.scheduled_at + timedelta(minutes=appt.duration_minutes) > data.scheduled_at
    ]

    if overlapping:
        raise ConflictError(
            f"Time slot conflicts with {len(overlapping)} existing appointment(s)"
        )

    appointment = model_class(
        scheduled_at=data.scheduled_at,
        duration_minutes=duration,
        status="pending",
        resource_id=data.resource_id,
        notes=data.notes,
    )
    session.add(appointment)
    await session.flush()

    return appointment


async def cancel_appointment(
    session: AsyncSession,
    appointment: Any,
) -> Any:
    """Cancel an existing appointment.

    Args:
        session: Active async database session.
        appointment: The appointment instance to cancel.

    Returns:
        The updated appointment instance.
    """
    appointment.cancel()
    await session.flush()
    return appointment


async def confirm_appointment(
    session: AsyncSession,
    appointment: Any,
) -> Any:
    """Confirm an existing appointment.

    Args:
        session: Active async database session.
        appointment: The appointment instance to confirm.

    Returns:
        The updated appointment instance.
    """
    appointment.confirm()
    await session.flush()
    return appointment
