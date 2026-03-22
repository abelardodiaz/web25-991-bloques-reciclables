"""Tests for two-way calendar sync functions."""

from datetime import UTC, datetime, timedelta

import pytest
from ulfblk_calendar import (
    CalendarEvent,
    sync_from_calendar,
    sync_to_calendar,
)


class TestSyncToCalendar:
    @pytest.mark.asyncio
    async def test_sync_creates_event(self, memory_provider, sample_event_create):
        result = await sync_to_calendar(sample_event_create, memory_provider)
        assert isinstance(result, CalendarEvent)
        assert result.title == sample_event_create.title

    @pytest.mark.asyncio
    async def test_sync_event_exists_in_provider(
        self, memory_provider, sample_event_create
    ):
        result = await sync_to_calendar(sample_event_create, memory_provider)
        now = datetime.now(tz=UTC)
        events = await memory_provider.list_events(
            now - timedelta(days=1), now + timedelta(days=1)
        )
        assert len(events) == 1
        assert events[0].external_id == result.external_id


class TestSyncFromCalendar:
    @pytest.mark.asyncio
    async def test_sync_returns_events(self, memory_provider, sample_event_create):
        await memory_provider.create_event(sample_event_create)
        now = datetime.now(tz=UTC)
        results = await sync_from_calendar(
            memory_provider, now - timedelta(days=1), now + timedelta(days=1)
        )
        assert len(results) == 1
        assert results[0].title == "Test Meeting"

    @pytest.mark.asyncio
    async def test_sync_empty_range(self, memory_provider):
        now = datetime.now(tz=UTC)
        results = await sync_from_calendar(
            memory_provider, now + timedelta(days=100), now + timedelta(days=101)
        )
        assert results == []
