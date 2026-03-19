"""Simple API example using bloque-core.

Run with:
    uv run uvicorn examples.api-simple.main:app --reload
    # or from the examples/api-simple directory:
    uv run uvicorn main:app --reload
"""

from bloque_core.health import health_router
from bloque_core.logging import setup_logging
from bloque_core.middleware import RequestIDMiddleware, TimingMiddleware
from fastapi import FastAPI

app = FastAPI(title="API Simple con Bloques")

setup_logging()

app.add_middleware(TimingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.include_router(health_router)


@app.get("/")
async def root():
    return {"message": "Funcionando con bloque-core"}


@app.get("/items")
async def list_items():
    return {
        "items": [
            {"id": 1, "name": "Example Item 1"},
            {"id": 2, "name": "Example Item 2"},
        ]
    }
