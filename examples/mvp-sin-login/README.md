# MVP sin Login - Example

Full-stack example: FastAPI backend + React frontend, zero auth.

## Backend

```bash
cd backend
uv add ulfblk-core
uv run uvicorn main:app --reload
# http://localhost:8000/docs
```

## Frontend

```bash
cd frontend
pnpm install
pnpm typecheck  # verify TypeScript compiles
```

## What this demonstrates

- `ulfblk-core`: API with health check, middleware, error handling
- `@ulfblk/api-client`: HTTP client with interceptors
- `@ulfblk/ui`: UI utilities (cn, preset)
- No auth, no DB - minimum viable product
