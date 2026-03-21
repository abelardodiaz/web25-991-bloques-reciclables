"""In-memory calendar provider for testing."""

import uuid
from datetime import datetime

from ..exceptions import CalendarSyncError
from ..schemas.event import CalendarEvent, EventCreate, EventUpdate


class InMemoryCalendarProvider:
    """In-memory calendar provider that stores events in a dictionary.

    Useful for testing and development without real calendar credentials.

    Example::

        provider = InMemoryCalendarProvider()
        event = await provider.create_event(
            EventCreate(title="Test", start=now, end=later)
        )
    """

    def __init__(self) -> None:
        self._events: dict[str, CalendarEvent] = {}

    async def create_event(self, event: EventCreate) -> CalendarEvent:
        """Create a new event and store it in memory.

        Args:
            event: The event data to create.

        Returns:
            The created event with a generated UUID as external_id.
        """
        external_id = str(uuid.uuid4())
        calendar_event = CalendarEvent(
            external_id=external_id,
            title=event.title,
            start=event.start,
            end=event.end,
            description=event.description,
            location=event.location,
            attendees=event.attendees,
        )
        self._events[external_id] = calendar_event
        return calendar_event

    async def update_event(self, event_id: str, event: EventUpdate) -> CalendarEvent:
        """Update an existing event in memory.

        Args:
            event_id: The external ID of the event to update.
            event: The fields to update. Only non-None fields are applied.

        Returns:
            The updated event.

        Raises:
            CalendarSyncError: If the event does not exist.
        """
        if event_id not in self._events:
            raise CalendarSyncError(f"Event not found: {event_id}")

        existing = self._events[event_id]
        update_data = event.model_dump(exclude_none=True)
        updated = existing.model_copy(update=update_data)
        self._events[event_id] = updated
        return updated

    async def delete_event(self, event_id: str) -> None:
        """Delete an event from memory.

        Args:
            event_id: The external ID of the event to delete.

        Raises:
            CalendarSyncError: If the event does not exist.
        """
        if event_id not in self._events:
            raise CalendarSyncError(f"Event not found: {event_id}")

        del self._events[event_id]

    async def list_events(self, start: datetime, end: datetime) -> list[CalendarEvent]:
        """List events within a time range.

        Args:
            start: The start of the time range (inclusive).
            end: The end of the time range (inclusive).

        Returns:
            A list of events whose start time falls within the range,
            sorted by start time.
        """
        matching = [
            event
            for event in self._events.values()
            if start <= event.start <= end
        ]
        return sorted(matching, key=lambda e: e.start)
