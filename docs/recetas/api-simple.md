# Receta: API Simple

> Con solo ulfblk-core tienes una API lista en minutos.

---

## Bloques necesarios

```bash
uv add ulfblk-core
```

## Que obtienes

- FastAPI con `create_app()` factory (middleware, health, exception handlers)
- Health check endpoint (/health)
- Logging estructurado con structlog
- Schemas base (PaginatedResponse, ErrorResponse, HealthResponse)
- Request ID y timing headers automaticos

## Setup rapido

```python
from ulfblk_core import create_app, get_logger, setup_logging
from ulfblk_core.schemas import PaginatedResponse

setup_logging()
logger = get_logger(__name__)

app = create_app(
    service_name="mi-api",
    version="0.1.0",
    title="Mi API",
)

@app.get("/items", response_model=PaginatedResponse[dict])
async def list_items(page: int = 1, size: int = 20):
    items = [{"id": i, "name": f"Item {i}"} for i in range(1, 21)]
    start = (page - 1) * size
    return PaginatedResponse.create(
        items=items[start : start + size],
        total=len(items),
        page=page,
        size=size,
    )
```

## Correr

```bash
uv run uvicorn main:app --reload
# -> http://localhost:8000/docs
# -> http://localhost:8000/health
```

## Que incluye create_app()

- RequestIDMiddleware (X-Request-ID header)
- TimingMiddleware (X-Process-Time header)
- Global exception handlers (HTTP, validation, generic -> ErrorResponse)
- Health router (/health)

## Siguiente paso

Agregar bloques segun necesidad:
- `ulfblk-auth` para autenticacion JWT
- `ulfblk-db` para base de datos con SQLAlchemy
- `ulfblk-multitenant` para soporte multi-inquilino
- `ulfblk-redis` para cache
