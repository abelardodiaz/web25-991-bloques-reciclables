# API Simple

Minimal FastAPI example using `bloque-core`.

## Run

```bash
cd examples/api-simple
uv run uvicorn main:app --reload
```

## Endpoints

- `GET /` - Root message
- `GET /health` - Health check
- `GET /items` - Example items

## What it demonstrates

- `RequestIDMiddleware` - Automatic X-Request-ID header
- `TimingMiddleware` - X-Process-Time header
- `health_router` - Standard /health endpoint
- `setup_logging` - Structured logging with request ID
