"""MVP sin Login - Backend.

Run with: cd examples/mvp-sin-login/backend && uv run uvicorn main:app --reload
"""

from fastapi.middleware.cors import CORSMiddleware

from ulfblk_core import create_app

app = create_app(service_name="mvp", version="0.1.0", title="MVP API")

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/data")
async def get_data():
    return {"items": ["uno", "dos", "tres"]}
