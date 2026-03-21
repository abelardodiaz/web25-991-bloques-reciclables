# ulfblk-calendar

Calendar integration for the Bloques ecosystem. Provides a pluggable provider protocol, Google Calendar sync, and an in-memory provider for testing.

## Installation

```bash
pip install ulfblk-calendar
```

For Google Calendar support:

```bash
pip install ulfblk-calendar[google]
```

## Quick Start

```python
from datetime import datetime, timedelta, timezone
from ulfblk_calendar import (
    CalendarSettings,
    InMemoryCalendarProvider,
    EventCreate,
    sync_to_calendar,
    sync_from_calendar,
)

# Create a provider (use InMemoryCalendarProvider for testing)
provider = InMemoryCalendarProvider()

# Create an event
now = datetime.now(tz=timezone.utc)
event = EventCreate(
    title="Team Standup",
    start=now + timedelta(hours=1),
    end=now + timedelta(hours=1, minutes=30),
    description="Daily standup meeting",
)

# Sync to calendar
import asyncio
created = asyncio.run(sync_to_calendar(event, provider))
print(f"Created: {created.external_id}")

# Sync from calendar
events = asyncio.run(sync_from_calendar(provider, now, now + timedelta(days=1)))
print(f"Found {len(events)} events")
```

## Custom Providers

Implement the `CalendarProvider` protocol to create your own backend:

```python
from ulfblk_calendar import CalendarProvider, CalendarEvent, EventCreate, EventUpdate
from datetime import datetime

class MyProvider:
    async def create_event(self, event: EventCreate) -> CalendarEvent: ...
    async def update_event(self, event_id: str, event: EventUpdate) -> CalendarEvent: ...
    async def delete_event(self, event_id: str) -> None: ...
    async def list_events(self, start: datetime, end: datetime) -> list[CalendarEvent]: ...
```
