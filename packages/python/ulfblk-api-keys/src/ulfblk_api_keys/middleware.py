"""FastAPI dependency for API key authentication."""

from __future__ import annotations

from fastapi import Header, HTTPException, Request

from .service import ApiKeyService


class ApiKeyAuth:
    """FastAPI Depends() callable for API key validation.

    Extracts key from X-API-Key header or ?api_key= query param.
    Attaches project_code and key_id to request.state.

    Args:
        service: ApiKeyService instance.
        required: If True (default), missing/invalid key raises 401.
                  If False, returns None for unauthenticated requests.

    Example::

        auth = ApiKeyAuth(service=key_service)

        @app.get("/api/data")
        async def get_data(key_data: dict = Depends(auth)):
            print(key_data["project_code"])
    """

    def __init__(self, service: ApiKeyService, required: bool = True) -> None:
        self.service = service
        self.required = required

    async def __call__(
        self,
        request: Request,
        x_api_key: str | None = Header(None),
    ) -> dict | None:
        raw_key = x_api_key or request.query_params.get("api_key")

        if not raw_key:
            if self.required:
                raise HTTPException(status_code=401, detail="API key required")
            return None

        # Get db session from request state (set by ulfblk-db middleware)
        db = getattr(request.state, "db", None)
        if db is None:
            raise HTTPException(
                status_code=500, detail="Database session not available",
            )

        key_data = await self.service.validate_key(db, raw_key)
        if key_data is None:
            raise HTTPException(status_code=401, detail="Invalid or expired API key")

        # Attach to request state for downstream use
        request.state.project_code = key_data["project_code"]
        request.state.project_name = key_data["project_name"]
        request.state.key_id = key_data["key_id"]

        return key_data
