"""ulfblk-calendar: Calendar integration for the Bloques ecosystem."""

__version__ = "0.1.0"

from .config.settings import CalendarSettings
from .exceptions import CalendarAuthError, CalendarSyncError
from .protocol.provider import CalendarProvider
from .providers.memory import InMemoryCalendarProvider
from .schemas.event import CalendarEvent, EventCreate, EventUpdate
from .sync.two_way import sync_from_calendar, sync_to_calendar

__all__ = [
    "CalendarAuthError",
    "CalendarEvent",
    "CalendarProvider",
    "CalendarSettings",
    "CalendarSyncError",
    "EventCreate",
    "EventUpdate",
    "InMemoryCalendarProvider",
    "sync_from_calendar",
    "sync_to_calendar",
]
