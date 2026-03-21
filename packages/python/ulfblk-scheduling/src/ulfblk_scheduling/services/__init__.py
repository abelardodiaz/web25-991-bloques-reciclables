"""Scheduling services: slot generation, conflict detection, and appointment management."""

from .conflict_checker import check_conflicts, is_within_advance_limits
from .scheduler import cancel_appointment, confirm_appointment, create_appointment
from .slot_generator import generate_slots

__all__ = [
    "cancel_appointment",
    "check_conflicts",
    "confirm_appointment",
    "create_appointment",
    "generate_slots",
    "is_within_advance_limits",
]
