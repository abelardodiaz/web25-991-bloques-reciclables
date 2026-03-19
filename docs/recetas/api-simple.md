# Receta: API Simple

> Con solo bloque-core tienes una API lista en minutos.

---

## Bloques necesarios

```bash
uv add bloque-core
```

## Que obtienes

- FastAPI con middleware stack (request ID, timing)
- Health check endpoint (/health)
- Logging estructurado con structlog
- Schemas base (PaginatedResponse, ErrorResponse)
- Listo para agregar mas bloques despues

## Setup rapido

```python
from fastapi import FastAPI
from bloque_core.middleware import RequestIDMiddleware, TimingMiddleware
from bloque_core.health import health_router
from bloque_core.logging import setup_logging
from bloque_core.schemas import PaginatedResponse

app = FastAPI(title="Mi API")
setup_logging()
app.add_middleware(RequestIDMiddleware)
app.add_middleware(TimingMiddleware)
app.include_router(health_router)

@app.get("/items", response_model=PaginatedResponse[dict])
async def list_items(page: int = 1, size: int = 20):
    items = [{"id": i, "name": f"Item {i}"} for i in range(1, 21)]
    return PaginatedResponse(
        items=items[(page-1)*size : page*size],
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

## Siguiente paso

Agregar bloques segun necesidad:
- `bloque-auth` para autenticacion JWT
- `bloque-multitenant` para soporte multi-inquilino
- `bloque-redis` para cache
