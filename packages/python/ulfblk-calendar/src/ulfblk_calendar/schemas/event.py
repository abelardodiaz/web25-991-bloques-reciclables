"""Pydantic models for calendar events."""

from datetime import datetime

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    """Schema for creating a new calendar event.

    All datetime fields must be timezone-aware.

    Example::

        event = EventCreate(
            title="Team Standup",
            start=datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc),
            end=datetime(2025, 1, 1, 9, 30, tzinfo=timezone.utc),
        )
    """

    title: str
    start: datetime
    end: datetime
    description: str = ""
    location: str = ""
    attendees: list[str] = Field(default_factory=list)


class EventUpdate(BaseModel):
    """Schema for updating an existing calendar event.

    All fields are optional. Only provided fields will be updated.
    Datetime fields must be timezone-aware when provided.

    Example::

        update = EventUpdate(title="Updated Standup")
    """

    title: str | None = None
    start: datetime | None = None
    end: datetime | None = None
    description: str | None = None
    location: str | None = None


class CalendarEvent(BaseModel):
    """Schema representing a calendar event as returned by a provider.

    Contains the external provider ID alongside event data.

    Example::

        event = CalendarEvent(
            external_id="abc123",
            title="Team Standup",
            start=datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc),
            end=datetime(2025, 1, 1, 9, 30, tzinfo=timezone.utc),
        )
    """

    external_id: str
    title: str
    start: datetime
    end: datetime
    description: str = ""
    location: str = ""
    attendees: list[str] = Field(default_factory=list)
