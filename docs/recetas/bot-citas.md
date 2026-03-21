# Receta: Bot de Citas

> Con ulfblk-core + ulfblk-db + ulfblk-scheduling + ulfblk-calendar construyes un bot de agendamiento.

---

## Bloques necesarios

```bash
uv add ulfblk-core ulfblk-db ulfblk-scheduling ulfblk-calendar aiosqlite
```

## Que obtienes

- FastAPI con `create_app()` factory (middleware, health, exception handlers)
- Base de datos async con SQLAlchemy (SQLite por defecto, PostgreSQL en produccion)
- Modelos composables con AppointmentMixin, AvailabilityMixin, BlockedSlotMixin
- Generacion automatica de horarios disponibles con `generate_slots()`
- Deteccion de conflictos con `check_conflicts()`
- Sincronizacion con calendario via InMemoryCalendarProvider (o Google Calendar)
- Bot conversacional con deteccion de intenciones por keywords

## Setup rapido

### 1. Modelos

```python
from sqlalchemy import Column, Integer, String
from ulfblk_db import Base, TimestampMixin
from ulfblk_scheduling import AppointmentMixin, AvailabilityMixin, BlockedSlotMixin

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
```

### 2. Database

```python
from ulfblk_db import DatabaseSettings, create_async_engine, create_session_factory, get_db_session
from models import Base

settings = DatabaseSettings(database_url="sqlite+aiosqlite:///./bot_citas.db")
engine = create_async_engine(settings)
SessionLocal = create_session_factory(engine)
db_dep = get_db_session(SessionLocal)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

### 3. App

```python
from contextlib import asynccontextmanager
from ulfblk_core import create_app

@asynccontextmanager
async def lifespan(app):
    await init_db()
    await seed_data(SessionLocal)
    yield

app = create_app(service_name="bot-citas", version="0.1.0", lifespan=lifespan)
```

### 4. Generar horarios disponibles

```python
from ulfblk_scheduling import generate_slots

slots = generate_slots(
    target_date=date(2026, 3, 23),
    availabilities=availabilities,  # from DB
    duration_minutes=30,
    existing_appointments=appointments,  # from DB
    blocked_slots=blocked,  # from DB
)
available = [s for s in slots if s.available]
```

### 5. Detectar conflictos

```python
from ulfblk_scheduling import check_conflicts

has_conflict = check_conflicts(
    start=scheduled_at,
    end=scheduled_at + timedelta(minutes=30),
    existing_appointments=existing,
)
if has_conflict:
    raise HTTPException(status_code=409, detail="Horario ocupado")
```

## Correr

```bash
cd examples/bot-citas
uv run uvicorn main:app --reload
# -> http://localhost:8000/docs
# -> http://localhost:8000/health
```

## Endpoints

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | /health | Health check |
| POST | /webhook | Bot conversacional |
| GET | /api/slots/{date} | Horarios disponibles para una fecha |
| POST | /api/appointments | Crear cita |
| DELETE | /api/appointments/{id} | Cancelar cita |

## Adaptar para tu negocio

### Consultorio medico
- Agregar `doctor_id` al modelo Appointment
- Usar `resource_id` del AvailabilityMixin para filtrar por doctor
- Agregar validacion de seguros

### Salon de belleza
- Agregar `service_type` con duraciones variables
- Multiples estilistas con `resource_id`
- Seed con horarios diferentes por dia

### Taller mecanico
- Agregar `vehicle_info` al modelo
- BlockedSlots para feriados y mantenimiento
- Duraciones mas largas (60-120 min)

### Produccion
- Cambiar SQLite por PostgreSQL: `BLOQUE_DATABASE_URL=postgresql+asyncpg://...`
- Reemplazar InMemoryCalendarProvider por Google Calendar
- Conectar un canal real (WhatsApp, Telegram) al endpoint /webhook
- Agregar ulfblk-auth para autenticacion
- Agregar ulfblk-notifications para recordatorios
