"""MVP sin Login - Backend.

Copied from docs/recetas/mvp-sin-login.md
Run with: uv run uvicorn main:app --reload
"""

from ulfblk_core import create_app

app = create_app(service_name="mvp", version="0.1.0", title="MVP API")


@app.get("/api/data")
async def get_data():
    return {"items": ["uno", "dos", "tres"]}
