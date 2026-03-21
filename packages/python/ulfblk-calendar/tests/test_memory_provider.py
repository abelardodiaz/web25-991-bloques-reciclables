"""Tests for InMemoryCalendarProvider."""

from datetime import datetime, timedelta, timezone

import pytest

from ulfblk_calendar import (
    CalendarEvent,
    EventCreate,
    EventUpdate,
    InMemoryCalendarProvider,
)
from ulfblk_calendar.exceptions import CalendarSyncError


class TestInMemoryCalendarProviderCreate:
    @pytest.mark.asyncio
    async def test_create_event(self, memory_provider, sample_event_create):
        result = await memory_provider.create_event(sample_event_create)
        assert isinstance(result, CalendarEvent)
        assert result.title == "Test Meeting"
        assert result.external_id != ""

    @pytest.mark.asyncio
    async def test_create_assigns_unique_ids(self, memory_provider):
        now = datetime.now(tz=timezone.utc)
        event = EventCreate(title="E1", start=now, end=now)
        r1 = await memory_provider.create_event(event)
        r2 = await memory_provider.create_event(event)
        assert r1.external_id != r2.external_id

    @pytest.mark.asyncio
    async def test_create_preserves_all_fields(self, memory_provider):
        now = datetime.now(tz=timezone.utc)
        event = EventCreate(
            title="Full",
            start=now,
            end=now,
            description="Desc",
            location="Loc",
            attendees=["a@b.com"],
        )
        result = await memory_provider.create_event(event)
        assert result.title == "Full"
        assert result.description == "Desc"
        assert result.location == "Loc"
        assert result.attendees == ["a@b.com"]


class TestInMemoryCalendarProviderUpdate:
    @pytest.mark.asyncio
    async def test_update_event(self, memory_provider, sample_event_create):
        created = await memory_provider.create_event(sample_event_create)
        update = EventUpdate(title="Updated Title")
        updated = await memory_provider.update_event(created.external_id, update)
        assert updated.title == "Updated Title"
        assert updated.description == created.description

    @pytest.mark.asyncio
    async def test_update_nonexistent_raises(self, memory_provider):
        with pytest.raises(CalendarSyncError, match="Event not found"):
            await memory_provider.update_event("fake-id", EventUpdate(title="X"))

    @pytest.mark.asyncio
    async def test_update_partial_fields(self, memory_provider, sample_event_create):
        created = await memory_provider.create_event(sample_event_create)
        update = EventUpdate(location="New Location")
        updated = await memory_provider.update_event(created.external_id, update)
        assert updated.location == "New Location"
        assert updated.title == created.title


class TestInMemoryCalendarProviderDelete:
    @pytest.mark.asyncio
    async def test_delete_event(self, memory_provider, sample_event_create):
        created = await memory_provider.create_event(sample_event_create)
        await memory_provider.delete_event(created.external_id)
        now = datetime.now(tz=timezone.utc)
        events = await memory_provider.list_events(
            now - timedelta(days=1), now + timedelta(days=1)
        )
        assert len(events) == 0

    @pytest.mark.asyncio
    async def test_delete_nonexistent_raises(self, memory_provider):
        with pytest.raises(CalendarSyncError, match="Event not found"):
            await memory_provider.delete_event("fake-id")


class TestInMemoryCalendarProviderList:
    @pytest.mark.asyncio
    async def test_list_events_in_range(self, memory_provider):
        base = datetime(2025, 6, 15, 10, 0, tzinfo=timezone.utc)
        e1 = EventCreate(title="E1", start=base, end=base + timedelta(hours=1))
        e2 = EventCreate(
            title="E2",
            start=base + timedelta(hours=2),
            end=base + timedelta(hours=3),
        )
        e3 = EventCreate(
            title="E3",
            start=base + timedelta(days=5),
            end=base + timedelta(days=5, hours=1),
        )
        await memory_provider.create_event(e1)
        await memory_provider.create_event(e2)
        await memory_provider.create_event(e3)

        results = await memory_provider.list_events(
            base - timedelta(hours=1),
            base + timedelta(hours=4),
        )
        assert len(results) == 2
        assert results[0].title == "E1"
        assert results[1].title == "E2"

    @pytest.mark.asyncio
    async def test_list_events_empty(self, memory_provider):
        now = datetime.now(tz=timezone.utc)
        results = await memory_provider.list_events(now, now + timedelta(hours=1))
        assert results == []

    @pytest.mark.asyncio
    async def test_list_events_sorted_by_start(self, memory_provider):
        base = datetime(2025, 6, 15, 10, 0, tzinfo=timezone.utc)
        late = EventCreate(
            title="Late",
            start=base + timedelta(hours=3),
            end=base + timedelta(hours=4),
        )
        early = EventCreate(
            title="Early",
            start=base + timedelta(hours=1),
            end=base + timedelta(hours=2),
        )
        await memory_provider.create_event(late)
        await memory_provider.create_event(early)

        results = await memory_provider.list_events(base, base + timedelta(hours=5))
        assert results[0].title == "Early"
        assert results[1].title == "Late"
