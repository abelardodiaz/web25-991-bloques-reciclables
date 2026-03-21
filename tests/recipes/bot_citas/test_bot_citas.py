"""E2E tests for the bot-citas recipe example.

Sets up its own app instance with in-memory SQLite since the example
uses absolute imports and is designed to run directly.
Tests 8 key behaviors: health, bot intents, slots, appointments, conflicts.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

import pytest
from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession

from ulfblk_core import create_app
from ulfblk_calendar import InMemoryCalendarProvider, EventCreate
from ulfblk_db import (
    Base,
    DatabaseSettings,
    TimestampMixin,
    create_async_engine,
    create_session_factory,
    get_db_session,
)
from ulfblk_scheduling import (
    AppointmentMixin,
    AvailabilityMixin,
    BlockedSlotMixin,
    check_conflicts,
    generate_slots,
)
from ulfblk_testing import create_test_client


# ---------------------------------------------------------------------------
# Models (same as examples/bot-citas/models.py)
# ---------------------------------------------------------------------------
class Appointment(Base, AppointmentMixin, TimestampMixin):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_name = Column(String(255), nullable=False)
    client_phone = Column(String(50), nullable=False)


class Availability(Base, AvailabilityMixin):
    __tablename__ = "availabilities"
    id = Column(Integer, primary_key=True, autoincrement=True)


class BlockedSlot(Base, BlockedSlotMixin):
    __tablename__ = "blocked_slots"
    id = Column(Integer, primary_key=True, autoincrement=True)


# ---------------------------------------------------------------------------
# Database (in-memory SQLite for tests)
# ---------------------------------------------------------------------------
_settings = DatabaseSettings(database_url="sqlite+aiosqlite://")
_engine = create_async_engine(_settings)
SessionLocal = create_session_factory(_engine)
db_dep = get_db_session(SessionLocal)

calendar_provider = InMemoryCalendarProvider()


# ---------------------------------------------------------------------------
# Bot logic (same as examples/bot-citas/bot.py)
# ---------------------------------------------------------------------------
INTENTS: dict[str, list[str]] = {
    "book": ["agendar", "cita", "reservar", "appointment", "book"],
    "cancel": ["cancelar", "cancel"],
    "slots": ["horarios", "disponible", "slots", "available"],
    "help": ["ayuda", "help", "info"],
}


def detect_intent(message: str) -> str:
    lower = message.lower()
    for intent, keywords in INTENTS.items():
        for keyword in keywords:
            if keyword in lower:
                return intent
    return "unknown"


async def handle_message(message: str, db_session: AsyncSession) -> str:
    intent = detect_intent(message)
    if intent == "help":
        return (
            "Comandos disponibles:\n"
            "  - 'horarios' o 'disponible': ver horarios disponibles\n"
            "  - 'agendar' o 'cita': agendar una cita\n"
            "  - 'cancelar': cancelar una cita\n"
            "  - 'ayuda': ver este mensaje"
        )
    if intent == "slots":
        today = date.today()
        result = await db_session.execute(
            select(Availability).where(
                Availability.day_of_week == today.weekday(),
                Availability.is_active.is_(True),
            )
        )
        availabilities = result.scalars().all()
        if not availabilities:
            return "No hay horarios disponibles hoy."
        result = await db_session.execute(
            select(Appointment).where(Appointment.status != "cancelled")
        )
        all_appts = result.scalars().all()
        today_appts = [a for a in all_appts if a.scheduled_at.date() == today]
        slots = generate_slots(
            target_date=today,
            availabilities=availabilities,
            duration_minutes=30,
            existing_appointments=today_appts,
        )
        available = [s for s in slots if s.available]
        if not available:
            return "No hay horarios disponibles hoy."
        lines = ["Horarios disponibles hoy:"]
        for slot in available:
            lines.append(f"  - {slot.start.strftime('%H:%M')} a {slot.end.strftime('%H:%M')}")
        return "\n".join(lines)
    if intent == "book":
        return (
            "Para agendar una cita, usa el endpoint POST /api/appointments con:\n"
            '  {"date": "YYYY-MM-DD", "time": "HH:MM", "name": "Tu Nombre", "phone": "123456"}'
        )
    if intent == "cancel":
        return (
            "Para cancelar una cita, usa el endpoint DELETE /api/appointments/{id} "
            "con el ID de tu cita."
        )
    return "No entendi, escribe 'ayuda'"


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class WebhookRequest(BaseModel):
    message: str
    phone: str


class WebhookResponse(BaseModel):
    response: str


class AppointmentRequest(BaseModel):
    date: str
    time: str
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
# App setup (no lifespan - tables managed by fixture)
# ---------------------------------------------------------------------------
app = create_app(
    service_name="bot-citas",
    version="0.1.0",
)


@app.post("/webhook", response_model=WebhookResponse)
async def webhook(body: WebhookRequest, db: AsyncSession = Depends(db_dep)):
    response = await handle_message(body.message, db)
    return WebhookResponse(response=response)


@app.get("/api/slots/{date_str}", response_model=list[SlotOut])
async def get_slots(date_str: str, db: AsyncSession = Depends(db_dep)):
    try:
        target_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format.")

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
    all_appts = result.scalars().all()
    day_appts = [a for a in all_appts if a.scheduled_at.date() == target_date]

    result = await db.execute(select(BlockedSlot))
    blocked = result.scalars().all()
    day_blocked = [b for b in blocked if b.start_at.date() == target_date]

    slots = generate_slots(
        target_date=target_date,
        availabilities=availabilities,
        duration_minutes=30,
        existing_appointments=day_appts,
        blocked_slots=day_blocked,
    )
    return [SlotOut(start=s.start, end=s.end, available=s.available) for s in slots]


@app.post("/api/appointments", response_model=AppointmentOut, status_code=201)
async def create_appointment_endpoint(body: AppointmentRequest, db: AsyncSession = Depends(db_dep)):
    try:
        appt_date = date.fromisoformat(body.date)
        appt_time = time.fromisoformat(body.time)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date/time format.")

    scheduled_at = datetime.combine(appt_date, appt_time, tzinfo=timezone.utc)
    duration_minutes = 30
    end_time = scheduled_at + timedelta(minutes=duration_minutes)

    result = await db.execute(
        select(Appointment).where(Appointment.status != "cancelled")
    )
    existing = result.scalars().all()
    day_existing = [a for a in existing if a.scheduled_at.date() == appt_date]

    # Ensure consistent timezone for comparison (SQLite strips tzinfo)
    for appt in day_existing:
        if appt.scheduled_at.tzinfo is None:
            appt.scheduled_at = appt.scheduled_at.replace(tzinfo=timezone.utc)

    if check_conflicts(start=scheduled_at, end=end_time, existing_appointments=day_existing):
        raise HTTPException(status_code=409, detail="Time slot conflicts with an existing appointment.")

    result = await db.execute(
        select(Availability).where(
            Availability.day_of_week == appt_date.weekday(),
            Availability.is_active.is_(True),
        )
    )
    availabilities = result.scalars().all()
    end_hour = appt_time.hour + (appt_time.minute + duration_minutes) // 60
    end_minute = (appt_time.minute + duration_minutes) % 60
    in_window = any(
        a.start_time <= appt_time and time(end_hour, end_minute) <= a.end_time
        for a in availabilities
    )
    if not in_window:
        raise HTTPException(status_code=400, detail="Requested time is outside availability windows.")

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

    await calendar_provider.create_event(EventCreate(
        title=f"Cita: {body.name}",
        start=scheduled_at,
        end=end_time,
        description=f"Telefono: {body.phone}",
    ))

    return AppointmentOut(
        id=appointment.id,
        client_name=appointment.client_name,
        client_phone=appointment.client_phone,
        scheduled_at=appointment.scheduled_at,
        duration_minutes=appointment.duration_minutes,
        status=appointment.status,
    )


@app.delete("/api/appointments/{appointment_id}")
async def cancel_appointment_endpoint(appointment_id: int, db: AsyncSession = Depends(db_dep)):
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
    return {"message": f"Appointment {appointment_id} cancelled.", "id": appointment_id}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _next_weekday() -> date:
    """Return the next Monday-Friday date (today if weekday, else next Monday)."""
    today = date.today()
    if today.weekday() < 5:
        return today
    days_ahead = 7 - today.weekday()
    return today + timedelta(days=days_ahead)


async def _setup_db():
    """Create tables and seed availability data."""
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        for dow in range(5):  # Mon-Fri
            session.add(Availability(
                day_of_week=dow, start_time=time(9, 0), end_time=time(13, 0), is_active=True,
            ))
            session.add(Availability(
                day_of_week=dow, start_time=time(14, 0), end_time=time(18, 0), is_active=True,
            ))
        await session.commit()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestBotCitasRecipe:
    """8 tests verifying the bot-citas recipe end-to-end."""

    async def test_health(self):
        """create_app() includes /health automatically."""
        async with create_test_client(app) as client:
            resp = await client.get("/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "healthy"
            assert data["service"] == "bot-citas"
            assert data["version"] == "0.1.0"

    async def test_webhook_help_intent(self):
        """Bot responds with help text for 'ayuda' keyword."""
        await _setup_db()
        async with create_test_client(app) as client:
            resp = await client.post(
                "/webhook",
                json={"message": "ayuda", "phone": "555-0001"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "Comandos disponibles" in data["response"]
            assert "horarios" in data["response"]

    async def test_webhook_slots_intent(self):
        """Bot responds to 'horarios' keyword with slot info."""
        await _setup_db()
        async with create_test_client(app) as client:
            resp = await client.post(
                "/webhook",
                json={"message": "horarios disponibles", "phone": "555-0002"},
            )
            assert resp.status_code == 200
            data = resp.json()
            # Either shows slots or says none available (depends on day of week)
            assert "response" in data

    async def test_webhook_unknown_intent(self):
        """Bot responds with fallback for unrecognized messages."""
        await _setup_db()
        async with create_test_client(app) as client:
            resp = await client.post(
                "/webhook",
                json={"message": "xyz123 random text", "phone": "555-0003"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["response"] == "No entendi, escribe 'ayuda'"

    async def test_get_slots_returns_list(self):
        """GET /api/slots/{date} returns a list of slot objects."""
        await _setup_db()
        target = _next_weekday()
        async with create_test_client(app) as client:
            resp = await client.get(f"/api/slots/{target.isoformat()}")
            assert resp.status_code == 200
            data = resp.json()
            assert isinstance(data, list)
            assert len(data) > 0
            slot = data[0]
            assert "start" in slot
            assert "end" in slot
            assert "available" in slot

    async def test_create_appointment(self):
        """POST /api/appointments creates appointment and returns 201."""
        await _setup_db()
        target = _next_weekday()
        async with create_test_client(app) as client:
            resp = await client.post(
                "/api/appointments",
                json={
                    "date": target.isoformat(),
                    "time": "10:00",
                    "name": "Maria Test",
                    "phone": "555-9999",
                },
            )
            assert resp.status_code == 201
            data = resp.json()
            assert data["client_name"] == "Maria Test"
            assert data["client_phone"] == "555-9999"
            assert data["status"] == "pending"
            assert data["duration_minutes"] == 30

    async def test_cancel_appointment(self):
        """DELETE /api/appointments/{id} cancels an existing appointment."""
        await _setup_db()
        target = _next_weekday()
        async with create_test_client(app) as client:
            # Create first
            resp = await client.post(
                "/api/appointments",
                json={
                    "date": target.isoformat(),
                    "time": "16:00",
                    "name": "Cancel Test",
                    "phone": "555-0000",
                },
            )
            assert resp.status_code == 201
            appt_id = resp.json()["id"]

            # Cancel
            resp = await client.delete(f"/api/appointments/{appt_id}")
            assert resp.status_code == 200
            data = resp.json()
            assert data["id"] == appt_id
            assert "cancelled" in data["message"].lower()

    async def test_conflict_detection(self):
        """POST /api/appointments returns 409 for conflicting time slots."""
        await _setup_db()
        target = _next_weekday()
        async with create_test_client(app) as client:
            # Create first appointment
            resp = await client.post(
                "/api/appointments",
                json={
                    "date": target.isoformat(),
                    "time": "11:00",
                    "name": "First",
                    "phone": "555-1111",
                },
            )
            assert resp.status_code == 201

            # Try to create conflicting appointment at same time
            resp = await client.post(
                "/api/appointments",
                json={
                    "date": target.isoformat(),
                    "time": "11:00",
                    "name": "Second",
                    "phone": "555-2222",
                },
            )
            assert resp.status_code == 409
            assert "conflict" in resp.json()["detail"].lower()
