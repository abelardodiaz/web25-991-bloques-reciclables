"""Pydantic schemas for scheduling."""

from .appointment import AppointmentCreate, AppointmentStatus, AppointmentUpdate
from .slot import Slot, TimeRange

__all__ = [
    "AppointmentCreate",
    "AppointmentStatus",
    "AppointmentUpdate",
    "Slot",
    "TimeRange",
]
