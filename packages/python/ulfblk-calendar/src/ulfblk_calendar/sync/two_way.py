"""Two-way calendar synchronization utilities."""

from datetime import datetime

from ..exceptions import CalendarSyncError
from ..protocol.provider import CalendarProvider
from ..schemas.event import CalendarEvent, EventCreate


async def sync_to_calendar(
    event_data: EventCreate,
    provider: CalendarProvider,
) -> CalendarEvent:
    """Sync an event to a calendar provider by creating it.

    Args:
        event_data: The event data to sync.
        provider: The calendar provider to sync to.

    Returns:
        The created calendar event with its external ID.

    Raises:
        CalendarSyncError: If the sync operation fails.
    """
    try:
        return await provider.create_event(event_data)
    except CalendarSyncError:
        raise
    except Exception as exc:
        raise CalendarSyncError(f"Failed to sync event to calendar: {exc}")


async def sync_from_calendar(
    provider: CalendarProvider,
    start: datetime,
    end: datetime,
) -> list[CalendarEvent]:
    """Sync events from a calendar provider within a time range.

    Args:
        provider: The calendar provider to sync from.
        start: The start of the time range.
        end: The end of the time range.

    Returns:
        A list of calendar events within the specified range.

    Raises:
        CalendarSyncError: If the sync operation fails.
    """
    try:
        return await provider.list_events(start, end)
    except CalendarSyncError:
        raise
    except Exception as exc:
        raise CalendarSyncError(f"Failed to sync events from calendar: {exc}")
