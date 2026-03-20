# bloque-core

Core utilities for building web APIs with FastAPI: middleware, schemas, structured logging, and health checks.

Part of [Bloques Reciclables](https://github.com/abelardodiaz/web25-991-bloques-reciclables) - an open source ecosystem of reusable code blocks.

## Installation

```bash
uv add bloque-core
# or
pip install bloque-core
```

## Features

### Middleware

**RequestIDMiddleware** - Distributed tracing via `X-Request-ID` header. Generates UUID4 if not present, propagates through contextvars for logging.

**TimingMiddleware** - Measures request duration and adds `X-Process-Time` header. Logs warnings for slow requests (>1s).

```python
from fastapi import FastAPI
from bloque_core.middleware import RequestIDMiddleware, TimingMiddleware

app = FastAPI()
app.add_middleware(TimingMiddleware)
app.add_middleware(RequestIDMiddleware)
```

### Schemas

Standardized Pydantic v2 schemas for API responses:

```python
from bloque_core.schemas import PaginatedResponse, ErrorResponse, SuccessResponse, HealthResponse

# Paginated response
response = PaginatedResponse.create(
    items=my_items,
    total=100,
    page=1,
    page_size=20,
)

# Health check
health = HealthResponse.healthy(service="my-api", version="1.0.0")
```

### Structured Logging

Structured logging with [structlog](https://www.structlog.org/), automatic request ID injection, and JSON/console output:

```python
from bloque_core.logging import setup_logging, get_logger

setup_logging(level="INFO", json_format=True, service_name="my-api")

logger = get_logger(__name__)
logger.info("user.created", user_id="123", tenant="acme")
# Output: {"event": "user.created", "user_id": "123", "request_id": "abc-def", ...}
```

### Health Check Router

Ready-to-use health check endpoint:

```python
from bloque_core.health import health_router

app.include_router(health_router)
# GET /health -> {"status": "healthy", "service": "api", "version": "0.1.0", ...}
```

## Full Example

```python
from fastapi import FastAPI
from bloque_core.middleware import RequestIDMiddleware, TimingMiddleware
from bloque_core.health import health_router
from bloque_core.logging import setup_logging

app = FastAPI(title="My API")
setup_logging()
app.add_middleware(TimingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.include_router(health_router)

@app.get("/")
async def root():
    return {"message": "Running with bloque-core"}
```

See the [api-simple example](https://github.com/abelardodiaz/web25-991-bloques-reciclables/tree/main/examples/api-simple) for a runnable version.

## Requirements

- Python 3.11+
- FastAPI 0.115+
- Pydantic 2.0+

## License

[MIT](https://github.com/abelardodiaz/web25-991-bloques-reciclables/blob/main/LICENSE)
