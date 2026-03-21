"""Application models using ulfblk-db and ulfblk-scheduling mixins.

Defines appointment, availability, and blocked slot models by composing
Base, TimestampMixin, AppointmentMixin, AvailabilityMixin, and BlockedSlotMixin.
"""

from __future__ import annotations

from sqlalchemy import Column, Integer, String

from ulfblk_db import Base, TimestampMixin
from ulfblk_scheduling import AppointmentMixin, AvailabilityMixin, BlockedSlotMixin


class Appointment(Base, AppointmentMixin, TimestampMixin):
    """Appointment model with client contact info."""

    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_name = Column(String(255), nullable=False)
    client_phone = Column(String(50), nullable=False)


class Availability(Base, AvailabilityMixin):
    """Recurring availability windows (weekly schedule)."""

    __tablename__ = "availabilities"

    id = Column(Integer, primary_key=True, autoincrement=True)


class BlockedSlot(Base, BlockedSlotMixin):
    """Blocked time slots (holidays, breaks, etc)."""

    __tablename__ = "blocked_slots"

    id = Column(Integer, primary_key=True, autoincrement=True)
