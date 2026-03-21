"""ulfblk-scheduling: Scheduling infrastructure for the Bloques ecosystem."""

__version__ = "0.1.0"

from .config.settings import SchedulingSettings
from .exceptions import ConflictError, SchedulingError, SlotUnavailableError
from .models.appointment import AppointmentMixin
from .models.availability import AvailabilityMixin
from .models.blocked_slot import BlockedSlotMixin
from .services.conflict_checker import check_conflicts, is_within_advance_limits
from .services.slot_generator import generate_slots

__all__ = [
    "AppointmentMixin",
    "AvailabilityMixin",
    "BlockedSlotMixin",
    "ConflictError",
    "SchedulingError",
    "SchedulingSettings",
    "SlotUnavailableError",
    "check_conflicts",
    "generate_slots",
    "is_within_advance_limits",
]
