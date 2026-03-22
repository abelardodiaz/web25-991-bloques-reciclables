"""Simple intent-based bot for appointment management.

Uses keyword matching for intent detection - no AI or external deps required.
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Appointment, Availability, BlockedSlot
from ulfblk_scheduling import generate_slots

INTENTS: dict[str, list[str]] = {
    "book": ["agendar", "cita", "reservar", "appointment", "book"],
    "cancel": ["cancelar", "cancel"],
    "slots": ["horarios", "disponible", "slots", "available"],
    "help": ["ayuda", "help", "info"],
}


def detect_intent(message: str) -> str:
    """Detect user intent from message keywords.

    Args:
        message: The user's message text.

    Returns:
        Intent name string, or "unknown" if no match.
    """
    lower = message.lower()
    for intent, keywords in INTENTS.items():
        for keyword in keywords:
            if keyword in lower:
                return intent
    return "unknown"


async def _get_today_slots(db: AsyncSession) -> str:
    """Build a string showing today's available time slots."""
    today = date.today()

    result = await db.execute(
        select(Availability).where(
            Availability.day_of_week == today.weekday(),
            Availability.is_active.is_(True),
        )
    )
    availabilities = result.scalars().all()

    if not availabilities:
        return "No hay horarios disponibles hoy."

    result = await db.execute(
        select(Appointment).where(
            Appointment.status != "cancelled",
        )
    )
    all_appointments = result.scalars().all()
    today_appointments = [
        a for a in all_appointments if a.scheduled_at.date() == today
    ]

    result = await db.execute(select(BlockedSlot))
    blocked = result.scalars().all()
    today_blocked = [b for b in blocked if b.start_at.date() == today]

    slots = generate_slots(
        target_date=today,
        availabilities=availabilities,
        duration_minutes=30,
        existing_appointments=today_appointments,
        blocked_slots=today_blocked,
    )

    available = [s for s in slots if s.available]
    if not available:
        return "No hay horarios disponibles hoy."

    lines = ["Horarios disponibles hoy:"]
    for slot in available:
        lines.append(f"  - {slot.start.strftime('%H:%M')} a {slot.end.strftime('%H:%M')}")
    return "\n".join(lines)


async def handle_message(message: str, db_session: AsyncSession) -> str:
    """Process a message and return a response string.

    Args:
        message: The user's message text.
        db_session: Active async database session.

    Returns:
        Response string for the user.
    """
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
        return await _get_today_slots(db_session)

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
