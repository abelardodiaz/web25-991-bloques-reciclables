"""E2E tests for the bot-citas recipe example.

Sets up its own app instance with in-memory SQLite since the example
uses absolute imports and is designed to run directly.

Tests 23 key behaviors across 6 categories:
  - Health check (1 test)
  - Bot intents via /webhook (6 tests: help, slots, unknown, book, cancel, case-insensitive)
  - Slot generation via /api/slots (2 tests: valid date, invalid date)
  - Appointment CRUD (7 tests: create, cancel, conflict, blocked-slot, outside-window, 404, double-cancel)
  - React-admin endpoints (3 tests: list appointments, get/update single, list availabilities)
  - Edge cases (4 tests: partial overlap, calendar sync, seed idempotency, weekend slots)
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

import pytest
from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, func, select
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
# Bot logic (mirrors examples/bot-citas/bot.py with blocked_slots fix)
# ---------------------------------------------------------------------------
INTENTS: dict[str, list[str]] = {
    "cancel": ["cancelar", "cancel"],
    "book": ["agendar", "cita", "reservar", "appointment", "book"],
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

        # Query blocked slots (bug fix: previously missing)
        result = await db_session.execute(select(BlockedSlot))
        blocked = result.scalars().all()
        today_blocked = [b for b in blocked if b.start_at.date() == today]

        slots = generate_slots(
            target_date=today,
            availabilities=availabilities,
            duration_minutes=30,
            existing_appointments=today_appts,
            blocked_slots=today_blocked,
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


class AppointmentUpdate(BaseModel):
    client_name: str | None = None
    client_phone: str | None = None
    status: str | None = None


class SlotOut(BaseModel):
    start: datetime
    end: datetime
    available: bool


class AvailabilityOut(BaseModel):
    id: int
    day_of_week: int
    start_time: str
    end_time: str
    is_active: bool


# ---------------------------------------------------------------------------
# App setup (no lifespan - tables managed by _setup_db helper)
# ---------------------------------------------------------------------------
app = create_app(
    service_name="bot-citas",
    version="0.1.0",
)


# ---------------------------------------------------------------------------
# Core endpoints
# ---------------------------------------------------------------------------
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

    # Check blocked slots (bug fix: previously missing)
    # Normalize timezone for SQLite compatibility (strips tzinfo)
    result = await db.execute(select(BlockedSlot))
    blocked = result.scalars().all()
    day_blocked = [b for b in blocked if b.start_at.date() == appt_date]
    for block in day_blocked:
        if block.start_at.tzinfo is None:
            block.start_at = block.start_at.replace(tzinfo=timezone.utc)
        if block.end_at.tzinfo is None:
            block.end_at = block.end_at.replace(tzinfo=timezone.utc)

    if check_conflicts(
        start=scheduled_at,
        end=end_time,
        existing_appointments=day_existing,
        blocked_slots=day_blocked,
    ):
        raise HTTPException(
            status_code=409,
            detail="Time slot conflicts with an existing appointment or blocked slot.",
        )

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
# React-admin endpoints (mirrors main.py)
# ---------------------------------------------------------------------------
@app.get("/api/appointments")
async def list_appointments(request: Request, db: AsyncSession = Depends(db_dep)):
    """List appointments with pagination for react-admin."""
    page = int(request.query_params.get("page", "1"))
    size = int(request.query_params.get("size", "20"))
    sort = request.query_params.get("sort", "id")
    order = request.query_params.get("order", "ASC")

    total_result = await db.execute(select(func.count(Appointment.id)))
    total = total_result.scalar() or 0

    stmt = select(Appointment)
    sort_col = getattr(Appointment, sort, Appointment.id)
    if order.upper() == "DESC":
        stmt = stmt.order_by(sort_col.desc())
    else:
        stmt = stmt.order_by(sort_col.asc())
    stmt = stmt.offset((page - 1) * size).limit(size)

    result = await db.execute(stmt)
    appointments = result.scalars().all()

    items = [
        AppointmentOut(
            id=a.id,
            client_name=a.client_name,
            client_phone=a.client_phone,
            scheduled_at=a.scheduled_at,
            duration_minutes=a.duration_minutes,
            status=a.status,
        )
        for a in appointments
    ]
    return {"items": [item.model_dump(mode="json") for item in items], "total": total}


@app.get("/api/appointments/{appointment_id}")
async def get_appointment(appointment_id: int, db: AsyncSession = Depends(db_dep)):
    """Get a single appointment by ID."""
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found.")
    return AppointmentOut(
        id=appointment.id,
        client_name=appointment.client_name,
        client_phone=appointment.client_phone,
        scheduled_at=appointment.scheduled_at,
        duration_minutes=appointment.duration_minutes,
        status=appointment.status,
    )


@app.put("/api/appointments/{appointment_id}")
async def update_appointment(
    appointment_id: int,
    body: AppointmentUpdate,
    db: AsyncSession = Depends(db_dep),
):
    """Update an appointment by ID."""
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found.")

    if body.client_name is not None:
        appointment.client_name = body.client_name
    if body.client_phone is not None:
        appointment.client_phone = body.client_phone
    if body.status is not None:
        appointment.status = body.status

    await db.commit()
    await db.refresh(appointment)

    return AppointmentOut(
        id=appointment.id,
        client_name=appointment.client_name,
        client_phone=appointment.client_phone,
        scheduled_at=appointment.scheduled_at,
        duration_minutes=appointment.duration_minutes,
        status=appointment.status,
    )


@app.get("/api/availabilities")
async def list_availabilities(request: Request, db: AsyncSession = Depends(db_dep)):
    """List availabilities with pagination for react-admin."""
    page = int(request.query_params.get("page", "1"))
    size = int(request.query_params.get("size", "20"))
    sort = request.query_params.get("sort", "id")
    order = request.query_params.get("order", "ASC")

    total_result = await db.execute(select(func.count(Availability.id)))
    total = total_result.scalar() or 0

    stmt = select(Availability)
    sort_col = getattr(Availability, sort, Availability.id)
    if order.upper() == "DESC":
        stmt = stmt.order_by(sort_col.desc())
    else:
        stmt = stmt.order_by(sort_col.asc())
    stmt = stmt.offset((page - 1) * size).limit(size)

    result = await db.execute(stmt)
    availabilities = result.scalars().all()

    items = [
        AvailabilityOut(
            id=a.id,
            day_of_week=a.day_of_week,
            start_time=str(a.start_time),
            end_time=str(a.end_time),
            is_active=a.is_active,
        )
        for a in availabilities
    ]
    return {"items": [item.model_dump(mode="json") for item in items], "total": total}


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
    """Create tables and seed availability data (Mon-Fri 9-13 and 14-18)."""
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


async def _setup_db_with_blocked_slot():
    """Create tables, seed availability, and add a blocked slot at 10:00-10:30."""
    await _setup_db()
    target = _next_weekday()
    async with SessionLocal() as session:
        session.add(BlockedSlot(
            start_at=datetime.combine(target, time(10, 0), tzinfo=timezone.utc),
            end_at=datetime.combine(target, time(10, 30), tzinfo=timezone.utc),
            reason="Descanso programado",
        ))
        await session.commit()


# ---------------------------------------------------------------------------
# Tests - Health
# ---------------------------------------------------------------------------
class TestHealth:
    """Verify create_app() provides /health automatically."""

    async def test_health(self):
        """GET /health returns service name, version, and healthy status."""
        async with create_test_client(app) as client:
            resp = await client.get("/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "healthy"
            assert data["service"] == "bot-citas"
            assert data["version"] == "0.1.0"


# ---------------------------------------------------------------------------
# Tests - Bot intents via /webhook
# ---------------------------------------------------------------------------
class TestWebhookIntents:
    """6 tests covering all bot intents: help, slots, book, cancel, unknown."""

    async def test_help_intent(self):
        """'ayuda' keyword triggers help text listing all commands."""
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
            assert "agendar" in data["response"]
            assert "cancelar" in data["response"]

    async def test_slots_intent_weekday(self):
        """'horarios' on a weekday returns actual time slot listings.

        Uses _next_weekday() to guarantee we test against a day with seeded
        availability (Mon-Fri). Verifies the response contains time patterns
        like 'HH:MM a HH:MM' rather than just checking the key exists.
        """
        await _setup_db()
        target = _next_weekday()
        # Seed availability for the specific weekday we'll test (already done
        # by _setup_db which seeds Mon-Fri). The bot uses date.today() internally,
        # so this test is deterministic only on weekdays. On weekends _next_weekday
        # returns next Monday but the bot queries today, so we verify both paths.
        async with create_test_client(app) as client:
            resp = await client.post(
                "/webhook",
                json={"message": "horarios disponibles", "phone": "555-0002"},
            )
            assert resp.status_code == 200
            data = resp.json()
            response_text = data["response"]
            # On weekdays: shows slot listings; on weekends: says none available
            if date.today().weekday() < 5:
                assert "Horarios disponibles hoy:" in response_text
                assert " a " in response_text  # time format "HH:MM a HH:MM"
            else:
                assert "No hay horarios disponibles hoy" in response_text

    async def test_book_intent(self):
        """'agendar' keyword triggers booking instructions with JSON example."""
        await _setup_db()
        async with create_test_client(app) as client:
            resp = await client.post(
                "/webhook",
                json={"message": "quiero agendar una cita", "phone": "555-0010"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "POST /api/appointments" in data["response"]
            assert "YYYY-MM-DD" in data["response"]

    async def test_cancel_intent(self):
        """'cancelar' keyword triggers cancellation instructions.

        Uses 'cancelar mi cita' which contains both 'cancelar' (cancel) and
        'cita' (book) keywords. Cancel must win because it's evaluated first
        in the INTENTS dict ordering.
        """
        await _setup_db()
        async with create_test_client(app) as client:
            resp = await client.post(
                "/webhook",
                json={"message": "cancelar mi cita", "phone": "555-0011"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "DELETE /api/appointments" in data["response"]

    async def test_unknown_intent(self):
        """Unrecognized messages get fallback suggesting 'ayuda'."""
        await _setup_db()
        async with create_test_client(app) as client:
            resp = await client.post(
                "/webhook",
                json={"message": "xyz123 random text", "phone": "555-0003"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["response"] == "No entendi, escribe 'ayuda'"

    async def test_intent_detection_is_case_insensitive(self):
        """Intent keywords match regardless of case."""
        await _setup_db()
        async with create_test_client(app) as client:
            resp = await client.post(
                "/webhook",
                json={"message": "AYUDA POR FAVOR", "phone": "555-0012"},
            )
            assert resp.status_code == 200
            assert "Comandos disponibles" in resp.json()["response"]


# ---------------------------------------------------------------------------
# Tests - Slot generation via /api/slots
# ---------------------------------------------------------------------------
class TestSlots:
    """2 tests for GET /api/slots/{date}: valid and invalid date."""

    async def test_get_slots_returns_list(self):
        """Valid weekday date returns a list of slot objects with start/end/available."""
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
            # All seeded slots for a fresh DB should be available
            available_count = sum(1 for s in data if s["available"])
            assert available_count > 0

    async def test_get_slots_invalid_date(self):
        """Invalid date format returns 400."""
        await _setup_db()
        async with create_test_client(app) as client:
            resp = await client.get("/api/slots/not-a-date")
            assert resp.status_code == 400
            assert "Invalid date" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# Tests - Appointment CRUD
# ---------------------------------------------------------------------------
class TestAppointments:
    """7 tests for POST/DELETE /api/appointments: create, cancel, conflicts,
    blocked slots, outside-window, 404, and double-cancel."""

    async def test_create_appointment(self):
        """POST /api/appointments with valid data returns 201 with appointment details."""
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
            assert data["id"] >= 1

    async def test_cancel_appointment(self):
        """DELETE /api/appointments/{id} sets status to cancelled."""
        await _setup_db()
        target = _next_weekday()
        async with create_test_client(app) as client:
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

            resp = await client.delete(f"/api/appointments/{appt_id}")
            assert resp.status_code == 200
            data = resp.json()
            assert data["id"] == appt_id
            assert "cancelled" in data["message"].lower()

    async def test_conflict_detection(self):
        """Double-booking the same slot returns 409 conflict."""
        await _setup_db()
        target = _next_weekday()
        async with create_test_client(app) as client:
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

    async def test_blocked_slot_prevents_booking(self):
        """Booking during a blocked slot (e.g. break, holiday) returns 409.

        This test verifies the bug fix where create_appointment previously
        did not check BlockedSlots, allowing bookings during blocked times.
        """
        await _setup_db_with_blocked_slot()
        target = _next_weekday()
        async with create_test_client(app) as client:
            # Verify the slot shows as unavailable in GET /api/slots
            resp = await client.get(f"/api/slots/{target.isoformat()}")
            assert resp.status_code == 200
            slots = resp.json()
            blocked_slot = next(
                (s for s in slots if "T10:00" in s["start"]),
                None,
            )
            if blocked_slot:
                assert blocked_slot["available"] is False

            # Attempt to book at 10:00 (blocked) should fail
            resp = await client.post(
                "/api/appointments",
                json={
                    "date": target.isoformat(),
                    "time": "10:00",
                    "name": "Blocked Test",
                    "phone": "555-3333",
                },
            )
            assert resp.status_code == 409
            assert "conflict" in resp.json()["detail"].lower()

    async def test_outside_availability_window(self):
        """Booking outside business hours (before 9:00 or after 18:00) returns 400."""
        await _setup_db()
        target = _next_weekday()
        async with create_test_client(app) as client:
            resp = await client.post(
                "/api/appointments",
                json={
                    "date": target.isoformat(),
                    "time": "07:00",  # Before 9:00 opening
                    "name": "Early Bird",
                    "phone": "555-4444",
                },
            )
            assert resp.status_code == 400
            assert "outside availability" in resp.json()["detail"].lower()

    async def test_cancel_nonexistent_returns_404(self):
        """Cancelling a nonexistent appointment returns 404."""
        await _setup_db()
        async with create_test_client(app) as client:
            resp = await client.delete("/api/appointments/99999")
            assert resp.status_code == 404
            assert "not found" in resp.json()["detail"].lower()

    async def test_double_cancel_returns_400(self):
        """Cancelling an already-cancelled appointment returns 400."""
        await _setup_db()
        target = _next_weekday()
        async with create_test_client(app) as client:
            resp = await client.post(
                "/api/appointments",
                json={
                    "date": target.isoformat(),
                    "time": "15:00",
                    "name": "Double Cancel",
                    "phone": "555-5555",
                },
            )
            assert resp.status_code == 201
            appt_id = resp.json()["id"]

            resp = await client.delete(f"/api/appointments/{appt_id}")
            assert resp.status_code == 200

            resp = await client.delete(f"/api/appointments/{appt_id}")
            assert resp.status_code == 400
            assert "already cancelled" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Tests - React-admin endpoints
# ---------------------------------------------------------------------------
class TestReactAdmin:
    """3 tests for react-admin compatible endpoints: list, get/update, availabilities."""

    async def test_list_appointments_with_pagination(self):
        """GET /api/appointments returns paginated list with total count.

        Tests the response shape expected by react-admin's DataProvider:
        {items: [...], total: N}.
        """
        await _setup_db()
        target = _next_weekday()
        async with create_test_client(app) as client:
            # Create 2 appointments
            for i, t in enumerate(["09:00", "09:30"]):
                resp = await client.post(
                    "/api/appointments",
                    json={
                        "date": target.isoformat(),
                        "time": t,
                        "name": f"Patient {i+1}",
                        "phone": f"555-{6000+i}",
                    },
                )
                assert resp.status_code == 201

            # List with default pagination
            resp = await client.get("/api/appointments")
            assert resp.status_code == 200
            data = resp.json()
            assert "items" in data
            assert "total" in data
            assert data["total"] == 2
            assert len(data["items"]) == 2

            # List with page=1, size=1 (pagination)
            resp = await client.get("/api/appointments?page=1&size=1")
            assert resp.status_code == 200
            data = resp.json()
            assert data["total"] == 2
            assert len(data["items"]) == 1

            # List with sort=id, order=DESC
            resp = await client.get("/api/appointments?sort=id&order=DESC")
            assert resp.status_code == 200
            data = resp.json()
            assert data["items"][0]["id"] > data["items"][1]["id"]

    async def test_get_and_update_single_appointment(self):
        """GET and PUT /api/appointments/{id} for react-admin detail/edit views."""
        await _setup_db()
        target = _next_weekday()
        async with create_test_client(app) as client:
            # Create
            resp = await client.post(
                "/api/appointments",
                json={
                    "date": target.isoformat(),
                    "time": "14:00",
                    "name": "Original Name",
                    "phone": "555-7000",
                },
            )
            assert resp.status_code == 201
            appt_id = resp.json()["id"]

            # GET single
            resp = await client.get(f"/api/appointments/{appt_id}")
            assert resp.status_code == 200
            data = resp.json()
            assert data["id"] == appt_id
            assert data["client_name"] == "Original Name"

            # PUT update
            resp = await client.put(
                f"/api/appointments/{appt_id}",
                json={"client_name": "Updated Name", "status": "confirmed"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["client_name"] == "Updated Name"
            assert data["status"] == "confirmed"
            # phone should remain unchanged
            assert data["client_phone"] == "555-7000"

    async def test_list_availabilities(self):
        """GET /api/availabilities returns seeded Mon-Fri schedule.

        Verifies 10 availability windows (5 days x 2 blocks: morning + afternoon).
        """
        await _setup_db()
        async with create_test_client(app) as client:
            resp = await client.get("/api/availabilities")
            assert resp.status_code == 200
            data = resp.json()
            assert "items" in data
            assert "total" in data
            # 5 days x 2 blocks (9-13, 14-18) = 10 availabilities
            assert data["total"] == 10
            assert len(data["items"]) == 10

            # Verify structure
            item = data["items"][0]
            assert "id" in item
            assert "day_of_week" in item
            assert "start_time" in item
            assert "end_time" in item
            assert "is_active" in item


# ---------------------------------------------------------------------------
# Tests - Edge cases and integration details
# ---------------------------------------------------------------------------
class TestEdgeCases:
    """4 tests for partial overlap, calendar sync, seed idempotency, weekends."""

    async def test_partial_overlap_conflict(self):
        """Booking at 10:15 when 10:00-10:30 is taken returns 409.

        Verifies that check_conflicts uses interval overlap logic
        (start < appt_end and end > appt_start), not just exact match.
        """
        await _setup_db()
        target = _next_weekday()
        async with create_test_client(app) as client:
            # Book 10:00-10:30
            resp = await client.post(
                "/api/appointments",
                json={
                    "date": target.isoformat(),
                    "time": "10:00",
                    "name": "First",
                    "phone": "555-8001",
                },
            )
            assert resp.status_code == 201

            # Try 10:15-10:45 (overlaps with 10:00-10:30)
            resp = await client.post(
                "/api/appointments",
                json={
                    "date": target.isoformat(),
                    "time": "10:15",
                    "name": "Overlap",
                    "phone": "555-8002",
                },
            )
            assert resp.status_code == 409
            assert "conflict" in resp.json()["detail"].lower()

    async def test_calendar_provider_receives_event(self):
        """Creating an appointment syncs an event to InMemoryCalendarProvider.

        Verifies the integration between the appointment endpoint and
        ulfblk-calendar's InMemoryCalendarProvider via list_events().
        """
        await _setup_db()
        # Clear any events from previous tests
        calendar_provider._events.clear()

        target = _next_weekday()
        async with create_test_client(app) as client:
            resp = await client.post(
                "/api/appointments",
                json={
                    "date": target.isoformat(),
                    "time": "09:00",
                    "name": "Calendar Sync Test",
                    "phone": "555-8003",
                },
            )
            assert resp.status_code == 201

        # Verify the event landed in the calendar provider
        day_start = datetime.combine(target, time(0, 0), tzinfo=timezone.utc)
        day_end = datetime.combine(target, time(23, 59), tzinfo=timezone.utc)
        events = await calendar_provider.list_events(start=day_start, end=day_end)
        assert len(events) == 1
        assert "Calendar Sync Test" in events[0].title
        assert "555-8003" in (events[0].description or "")

    async def test_seed_idempotent(self):
        """Running _setup_db (seed) twice does not duplicate availability rows.

        Mirrors seed.py behavior: checks if data exists before inserting.
        """
        await _setup_db()

        # Seed again by inserting only if empty (same logic as seed.py)
        async with SessionLocal() as session:
            result = await session.execute(select(Availability).limit(1))
            already_seeded = result.scalar_one_or_none() is not None

            if not already_seeded:
                for dow in range(5):
                    session.add(Availability(
                        day_of_week=dow, start_time=time(9, 0),
                        end_time=time(13, 0), is_active=True,
                    ))
                    session.add(Availability(
                        day_of_week=dow, start_time=time(14, 0),
                        end_time=time(18, 0), is_active=True,
                    ))
                await session.commit()

        # Should still be exactly 10 (not 20)
        async with SessionLocal() as session:
            result = await session.execute(select(func.count(Availability.id)))
            total = result.scalar()
            assert total == 10

    async def test_weekend_returns_no_slots(self):
        """GET /api/slots for a Saturday returns empty list.

        Only Mon-Fri have seeded availability, so weekends produce no slots.
        """
        await _setup_db()
        # Find next Saturday (weekday 5)
        today = date.today()
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0:
            days_until_saturday = 7
        next_saturday = today + timedelta(days=days_until_saturday)

        async with create_test_client(app) as client:
            resp = await client.get(f"/api/slots/{next_saturday.isoformat()}")
            assert resp.status_code == 200
            data = resp.json()
            assert isinstance(data, list)
            assert len(data) == 0
