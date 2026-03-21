"""Tests for scheduling exceptions."""

from ulfblk_scheduling import ConflictError, SchedulingError, SlotUnavailableError


class TestExceptions:
    def test_scheduling_error_is_exception(self):
        assert issubclass(SchedulingError, Exception)

    def test_slot_unavailable_is_scheduling_error(self):
        assert issubclass(SlotUnavailableError, SchedulingError)

    def test_conflict_error_is_scheduling_error(self):
        assert issubclass(ConflictError, SchedulingError)

    def test_slot_unavailable_message(self):
        err = SlotUnavailableError("Slot taken")
        assert str(err) == "Slot taken"

    def test_conflict_error_message(self):
        err = ConflictError("Overlapping appointment")
        assert str(err) == "Overlapping appointment"
