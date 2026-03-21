"""Scheduling-specific exceptions."""


class SchedulingError(Exception):
    """Base exception for all scheduling-related errors.

    Example::

        raise SchedulingError("Unexpected scheduling failure")
    """

    pass


class SlotUnavailableError(SchedulingError):
    """Raised when a requested time slot is not available.

    Example::

        raise SlotUnavailableError("Slot 2024-01-15 10:00 is already taken")
    """

    pass


class ConflictError(SchedulingError):
    """Raised when a scheduling conflict is detected.

    Example::

        raise ConflictError("Appointment overlaps with existing booking")
    """

    pass
