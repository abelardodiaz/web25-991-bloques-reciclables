"""Pydantic schemas for appointment operations."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class AppointmentStatus(StrEnum):
    """Valid appointment statuses."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class AppointmentCreate(BaseModel):
    """Schema for creating a new appointment.

    Attributes:
        scheduled_at: When the appointment is scheduled.
        duration_minutes: Duration in minutes.
        resource_id: Optional resource identifier (doctor, room, etc).
        notes: Optional notes for the appointment.
    """

    scheduled_at: datetime
    duration_minutes: int = Field(default=30, gt=0)
    resource_id: str | None = None
    notes: str | None = None


class AppointmentUpdate(BaseModel):
    """Schema for updating an existing appointment.

    Attributes:
        scheduled_at: New scheduled time (optional).
        duration_minutes: New duration in minutes (optional).
        status: New status (optional).
        resource_id: New resource identifier (optional).
        notes: New notes (optional).
    """

    scheduled_at: datetime | None = None
    duration_minutes: int | None = Field(default=None, gt=0)
    status: AppointmentStatus | None = None
    resource_id: str | None = None
    notes: str | None = None
