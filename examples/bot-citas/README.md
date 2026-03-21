# Bot de Citas - Appointment Booking Bot

Example project demonstrating 4 ulfblk packages composing together to build
a generic appointment booking bot.

## Bloques used

| Bloque | Purpose |
|--------|---------|
| ulfblk-core | App factory, middleware, health check, schemas |
| ulfblk-db | SQLAlchemy async engine, Base, TimestampMixin |
| ulfblk-scheduling | AppointmentMixin, AvailabilityMixin, slot generation, conflict detection |
| ulfblk-calendar | InMemoryCalendarProvider for calendar sync demo |

## How to run

```bash
cd examples/bot-citas
uv run uvicorn main:app --reload
```

Or use the start script:

```bash
./start.sh
```

The API will be available at http://localhost:8000.

## Endpoints

- `GET /health` - Health check
- `POST /webhook` - Bot conversation (intent-based)
- `GET /api/slots/{date}` - Available slots for a date (YYYY-MM-DD)
- `POST /api/appointments` - Create an appointment
- `DELETE /api/appointments/{id}` - Cancel an appointment

## Example curl commands

### Check health

```bash
curl http://localhost:8000/health
```

### Talk to the bot

```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"message": "horarios disponibles", "phone": "555-1234"}'
```

### Get available slots for a date

```bash
curl http://localhost:8000/api/slots/2026-03-23
```

### Create an appointment

```bash
curl -X POST http://localhost:8000/api/appointments \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-03-23", "time": "09:00", "name": "Juan Perez", "phone": "555-1234"}'
```

### Cancel an appointment

```bash
curl -X DELETE http://localhost:8000/api/appointments/1
```

## Adapting for your business

This example uses generic naming. To adapt for a specific business:

1. Add domain-specific fields to the `Appointment` model (e.g., `service_type`, `provider_id`)
2. Modify `seed.py` to match your business hours
3. Extend `bot.py` intent keywords for your domain vocabulary
4. Replace `InMemoryCalendarProvider` with a real provider (e.g., Google Calendar)
5. Connect a real messaging channel (WhatsApp, Telegram) to the `/webhook` endpoint
