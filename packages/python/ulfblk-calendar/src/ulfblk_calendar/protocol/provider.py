"""CalendarProvider protocol for pluggable calendar backends."""

from datetime import datetime
from typing import Protocol

from ..schemas.event import CalendarEvent, EventCreate, EventUpdate


class CalendarProvider(Protocol):
    """Protocol defining the interface for calendar providers.

    Any class implementing this protocol can be used as a calendar backend.
    Implementations must provide async methods for CRUD operations on events.

    Example::

        class MyProvider:
            async def create_event(self, event: EventCreate) -> CalendarEvent:
                ...

            async def update_event(self, event_id: str, event: EventUpdate) -> CalendarEvent:
                ...

            async def delete_event(self, event_id: str) -> None:
                ...

            async def list_events(self, start: datetime, end: datetime) -> list[CalendarEvent]:
                ...
    """

    async def create_event(self, event: EventCreate) -> CalendarEvent:
        """Create a new event in the calendar.

        Args:
            event: The event data to create.

        Returns:
            The created event with its external ID assigned.
        """
        ...

    async def update_event(self, event_id: str, event: EventUpdate) -> CalendarEvent:
        """Update an existing event in the calendar.

        Args:
            event_id: The external ID of the event to update.
            event: The fields to update.

        Returns:
            The updated event.
        """
        ...

    async def delete_event(self, event_id: str) -> None:
        """Delete an event from the calendar.

        Args:
            event_id: The external ID of the event to delete.
        """
        ...

    async def list_events(self, start: datetime, end: datetime) -> list[CalendarEvent]:
        """List events within a time range.

        Args:
            start: The start of the time range (inclusive).
            end: The end of the time range (inclusive).

        Returns:
            A list of events within the specified range.
        """
        ...
