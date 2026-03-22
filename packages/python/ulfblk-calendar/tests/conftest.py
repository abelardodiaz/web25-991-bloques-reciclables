"""Shared fixtures for ulfblk-calendar tests."""

from datetime import UTC, datetime, timedelta

import pytest
from ulfblk_calendar import CalendarSettings, EventCreate, InMemoryCalendarProvider


@pytest.fixture
def calendar_settings() -> CalendarSettings:
    """CalendarSettings with defaults."""
    return CalendarSettings()


@pytest.fixture
def memory_provider() -> InMemoryCalendarProvider:
    """Fresh in-memory calendar provider."""
    return InMemoryCalendarProvider()


@pytest.fixture
def sample_event_create() -> EventCreate:
    """Sample EventCreate for tests."""
    now = datetime.now(tz=UTC)
    return EventCreate(
        title="Test Meeting",
        start=now + timedelta(hours=1),
        end=now + timedelta(hours=2),
        description="A test meeting",
        location="Conference Room A",
        attendees=["alice@example.com", "bob@example.com"],
    )
