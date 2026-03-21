"""Pydantic schemas for time slots and time ranges."""

from __future__ import annotations

from datetime import datetime, time

from pydantic import BaseModel


class Slot(BaseModel):
    """Represents a schedulable time slot.

    Attributes:
        start: Start datetime of the slot.
        end: End datetime of the slot.
        available: Whether the slot is available for booking.
    """

    start: datetime
    end: datetime
    available: bool = True


class TimeRange(BaseModel):
    """Represents a time range within a day.

    Attributes:
        start_time: Start time of the range.
        end_time: End time of the range.
    """

    start_time: time
    end_time: time
