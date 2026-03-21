"""Bot de Citas API - Appointment Booking Bot Example.

Demonstrates 4 bloques working together:
- ulfblk-core: App factory, middleware, schemas, health check
- ulfblk-db: SQLAlchemy models with composable mixins, async engine
- ulfblk-scheduling: Slot generation, conflict detection, appointment mixins
- ulfblk-calendar: InMemoryCalendarProvider for calendar sync demo

Uses SQLite by default (zero config). For PostgreSQL:
    export BLOQUE_DATABASE_URL=postgresql+asyncpg://user:pass@localhost/mydb

Run with:
    cd examples/bot-citas
    uv run uvicorn main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date, datetime, time, timedelta, timezone

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ulfblk_core import create_app, get_logger, setup_logging
from ulfblk_calendar import InMemoryCalendarProvider, EventCreate
from ulfblk_scheduling import generate_slots, check_conflicts

from bot import handle_message
from database import SessionLocal, db_dep, init_db
from models import Appointment, Availability, BlockedSlot
from seed import seed_data

setup_logging(level="INFO")
logger = get_logger(__name__)

calendar_provider = InMemoryCalendarProvider()


# ---------------------------------------------------------------------------
# Lifespan: init DB + seed data
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app):
    await init_db()
    await seed_data(SessionLocal)
    logger.info("database.ready", msg="Tables created and availability seeded")
    yield


# ---------------------------------------------------------------------------
# App (using create_app from ulfblk-core)
# ---------------------------------------------------------------------------
app = create_app(
    service_name="bot-citas",
    version="0.1.0",
    title="Bot de Citas",
    description="Appointment booking bot using ulfblk-core + ulfblk-db + ulfblk-scheduling + ulfblk-calendar",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class WebhookRequest(BaseModel):
    message: str
    phone: str


class WebhookResponse(BaseModel):
    response: str


class AppointmentRequest(BaseModel):
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    name: str
    phone: str


class AppointmentOut(BaseModel):
    id: int
    client_name: str
    client_phone: str
    scheduled_at: datetime
    duration_minutes: int
    status: str


class SlotOut(BaseModel):
    start: datetime
    end: datetime
    available: bool


# ---------------------------------------------------------------------------
# Webhook endpoint (bot conversation)
# ---------------------------------------------------------------------------
@app.post("/webhook", response_model=WebhookResponse)
async def webhook(body: WebhookRequest, db: AsyncSession = Depends(db_dep)):
    """Receive a message and return bot response."""
    response = await handle_message(body.message, db)
    return WebhookResponse(response=response)


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------
@app.get("/api/slots/{date_str}", response_model=list[SlotOut])
async def get_slots(date_str: str, db: AsyncSession = Depends(db_dep)):
    """Return available slots for a given date (YYYY-MM-DD)."""
    try:
        target_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    result = await db.execute(
        select(Availability).where(
            Availability.day_of_week == target_date.weekday(),
            Availability.is_active.is_(True),
        )
    )
    availabilities = result.scalars().all()

    result = await db.execute(
        select(Appointment).where(Appointment.status != "cancelled")
    )
    all_appointments = result.scalars().all()
    day_appointments = [
        a for a in all_appointments if a.scheduled_at.date() == target_date
    ]

    result = await db.execute(select(BlockedSlot))
    blocked = result.scalars().all()
    day_blocked = [
        b for b in blocked if b.start_at.date() == target_date
    ]

    slots = generate_slots(
        target_date=target_date,
        availabilities=availabilities,
        duration_minutes=30,
        existing_appointments=day_appointments,
        blocked_slots=day_blocked,
    )

    return [SlotOut(start=s.start, end=s.end, available=s.available) for s in slots]


@app.post("/api/appointments", response_model=AppointmentOut, status_code=201)
async def create_appointment(body: AppointmentRequest, db: AsyncSession = Depends(db_dep)):
    """Create a new appointment."""
    try:
        appt_date = date.fromisoformat(body.date)
        appt_time = time.fromisoformat(body.time)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date/time format. Use YYYY-MM-DD and HH:MM.",
        )

    scheduled_at = datetime.combine(appt_date, appt_time, tzinfo=timezone.utc)
    duration_minutes = 30
    end_time = scheduled_at + timedelta(minutes=duration_minutes)

    # Check for conflicts
    result = await db.execute(
        select(Appointment).where(Appointment.status != "cancelled")
    )
    existing = result.scalars().all()
    day_existing = [
        a for a in existing if a.scheduled_at.date() == appt_date
    ]

    # Ensure consistent timezone for comparison (SQLite strips tzinfo)
    for appt in day_existing:
        if appt.scheduled_at.tzinfo is None:
            appt.scheduled_at = appt.scheduled_at.replace(tzinfo=timezone.utc)

    has_conflict = check_conflicts(
        start=scheduled_at,
        end=end_time,
        existing_appointments=day_existing,
    )
    if has_conflict:
        raise HTTPException(
            status_code=409,
            detail="Time slot conflicts with an existing appointment.",
        )

    # Check availability
    result = await db.execute(
        select(Availability).where(
            Availability.day_of_week == appt_date.weekday(),
            Availability.is_active.is_(True),
        )
    )
    availabilities = result.scalars().all()

    in_window = any(
        a.start_time <= appt_time and time(
            appt_time.hour + (appt_time.minute + duration_minutes) // 60,
            (appt_time.minute + duration_minutes) % 60,
        ) <= a.end_time
        for a in availabilities
    )
    if not in_window:
        raise HTTPException(
            status_code=400,
            detail="Requested time is outside availability windows.",
        )

    appointment = Appointment(
        client_name=body.name,
        client_phone=body.phone,
        scheduled_at=scheduled_at,
        duration_minutes=duration_minutes,
        status="pending",
    )
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)

    # Sync to calendar provider
    await calendar_provider.create_event(EventCreate(
        title=f"Cita: {body.name}",
        start=scheduled_at,
        end=end_time,
        description=f"Telefono: {body.phone}",
    ))

    logger.info(
        "appointment.created",
        appointment_id=appointment.id,
        client=body.name,
        scheduled_at=str(scheduled_at),
    )

    return AppointmentOut(
        id=appointment.id,
        client_name=appointment.client_name,
        client_phone=appointment.client_phone,
        scheduled_at=appointment.scheduled_at,
        duration_minutes=appointment.duration_minutes,
        status=appointment.status,
    )


@app.delete("/api/appointments/{appointment_id}")
async def cancel_appointment(appointment_id: int, db: AsyncSession = Depends(db_dep)):
    """Cancel an appointment by ID."""
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()

    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found.")

    if appointment.status == "cancelled":
        raise HTTPException(status_code=400, detail="Appointment already cancelled.")

    appointment.cancel()
    await db.commit()

    logger.info("appointment.cancelled", appointment_id=appointment_id)

    return {"message": f"Appointment {appointment_id} cancelled.", "id": appointment_id}
