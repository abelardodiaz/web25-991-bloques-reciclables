"""Tests for calendar event schemas."""

from datetime import datetime, timezone

from ulfblk_calendar import CalendarEvent, EventCreate, EventUpdate


class TestEventCreate:
    def test_minimal_fields(self):
        now = datetime.now(tz=timezone.utc)
        event = EventCreate(title="Test", start=now, end=now)
        assert event.title == "Test"
        assert event.start == now
        assert event.end == now
        assert event.description == ""
        assert event.location == ""
        assert event.attendees == []

    def test_all_fields(self):
        now = datetime.now(tz=timezone.utc)
        event = EventCreate(
            title="Full Event",
            start=now,
            end=now,
            description="A full event",
            location="Room 42",
            attendees=["a@b.com"],
        )
        assert event.title == "Full Event"
        assert event.description == "A full event"
        assert event.location == "Room 42"
        assert event.attendees == ["a@b.com"]


class TestEventUpdate:
    def test_all_optional(self):
        update = EventUpdate()
        assert update.title is None
        assert update.start is None
        assert update.end is None
        assert update.description is None
        assert update.location is None

    def test_partial_update(self):
        update = EventUpdate(title="New Title")
        assert update.title == "New Title"
        assert update.start is None


class TestCalendarEvent:
    def test_full_event(self):
        now = datetime.now(tz=timezone.utc)
        event = CalendarEvent(
            external_id="abc-123",
            title="Meeting",
            start=now,
            end=now,
            description="Desc",
            location="Here",
            attendees=["x@y.com"],
        )
        assert event.external_id == "abc-123"
        assert event.title == "Meeting"
        assert event.attendees == ["x@y.com"]

    def test_defaults(self):
        now = datetime.now(tz=timezone.utc)
        event = CalendarEvent(
            external_id="id-1",
            title="Minimal",
            start=now,
            end=now,
        )
        assert event.description == ""
        assert event.location == ""
        assert event.attendees == []
