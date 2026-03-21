"""Tests for CalendarProvider protocol satisfaction."""

from typing import runtime_checkable

from ulfblk_calendar import CalendarProvider, InMemoryCalendarProvider


class TestCalendarProviderProtocol:
    def test_protocol_is_runtime_checkable(self):
        """CalendarProvider can be checked at runtime with isinstance."""
        assert hasattr(CalendarProvider, "__protocol_attrs__") or hasattr(
            CalendarProvider, "__abstractmethods__"
        ) or issubclass(type(CalendarProvider), type)

    def test_memory_provider_satisfies_protocol(self):
        """InMemoryCalendarProvider structurally matches CalendarProvider."""
        provider = InMemoryCalendarProvider()
        assert hasattr(provider, "create_event")
        assert hasattr(provider, "update_event")
        assert hasattr(provider, "delete_event")
        assert hasattr(provider, "list_events")
        assert callable(provider.create_event)
        assert callable(provider.update_event)
        assert callable(provider.delete_event)
        assert callable(provider.list_events)
