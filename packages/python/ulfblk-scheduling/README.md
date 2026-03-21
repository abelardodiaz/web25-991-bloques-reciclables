# ulfblk-scheduling

Scheduling infrastructure for the Bloques ecosystem: appointment management, availability windows, slot generation, and conflict detection.

## Features

- **AppointmentMixin** - SQLAlchemy mixin for appointment models with status transitions
- **AvailabilityMixin** - Recurring weekly availability windows
- **BlockedSlotMixin** - Blocked time ranges (holidays, breaks)
- **Slot Generator** - Pure function to compute available time slots
- **Conflict Checker** - Detect scheduling conflicts and validate advance booking limits
- **Scheduler Service** - Async appointment lifecycle with concurrency-safe creation

## Quick Start

```python
from ulfblk_scheduling import (
    SchedulingSettings,
    AppointmentMixin,
    AvailabilityMixin,
    generate_slots,
    check_conflicts,
)
```

## Installation

```bash
uv add ulfblk-scheduling
```
