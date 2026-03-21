"""Tests for calendar exceptions."""

from ulfblk_calendar import CalendarAuthError, CalendarSyncError


class TestCalendarExceptions:
    def test_sync_error_default_message(self):
        exc = CalendarSyncError()
        assert str(exc) == "Calendar sync operation failed"
        assert exc.message == "Calendar sync operation failed"

    def test_sync_error_custom_message(self):
        exc = CalendarSyncError("Custom error")
        assert str(exc) == "Custom error"

    def test_auth_error_default_message(self):
        exc = CalendarAuthError()
        assert str(exc) == "Calendar authentication failed"
        assert exc.message == "Calendar authentication failed"

    def test_auth_error_custom_message(self):
        exc = CalendarAuthError("Bad creds")
        assert str(exc) == "Bad creds"

    def test_sync_error_is_exception(self):
        assert issubclass(CalendarSyncError, Exception)

    def test_auth_error_is_exception(self):
        assert issubclass(CalendarAuthError, Exception)
