"""FastAPI router for API key management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import KeyInfo, KeyResponse, RegisterRequest, RotateRequest
from .service import ApiKeyService


def create_api_keys_router(
    service: ApiKeyService,
    db_dependency: any,
) -> APIRouter:
    """Create a FastAPI router for key management.

    Args:
        service: ApiKeyService instance.
        db_dependency: FastAPI Depends() for database session.

    Returns:
        APIRouter with /keys/register, /keys/rotate, /keys/info.

    Example::

        from ulfblk_api_keys import ApiKeyService, create_api_keys_router
        from database import db_dep

        service = ApiKeyService(config=config, cache=cache)
        router = create_api_keys_router(service, db_dep)
        app.include_router(router)
    """

    router = APIRouter(prefix="/keys", tags=["API Keys"])

    @router.post("/register", response_model=KeyResponse)
    async def register_key(
        body: RegisterRequest, db: AsyncSession = Depends(db_dependency),
    ) -> KeyResponse:
        """Register a new API key. Requires master secret. Key shown once."""
        try:
            raw_key = await service.register_key(
                db,
                project_code=body.project_code,
                project_name=body.project_name,
                secret=body.secret,
            )
        except ValueError as e:
            raise HTTPException(status_code=403, detail=str(e))

        from sqlalchemy import select

        from .models import ApiKeyModel
        from .service import _hash_key

        key_hash = _hash_key(raw_key)
        result = await db.execute(
            select(ApiKeyModel).where(ApiKeyModel.key_hash == key_hash)
        )
        key_record = result.scalar_one()

        return KeyResponse(
            api_key=raw_key,
            key_id=key_record.id,
            project_code=key_record.project_code,
            created_at=key_record.created_at,
        )

    @router.post("/rotate", response_model=KeyResponse)
    async def rotate_key(
        body: RotateRequest, db: AsyncSession = Depends(db_dependency),
    ) -> KeyResponse:
        """Rotate API key. Old key valid for grace period."""
        try:
            raw_key = await service.rotate_key(
                db,
                project_code=body.project_code,
                old_raw_key=body.old_api_key,
                secret=body.secret,
            )
        except ValueError as e:
            raise HTTPException(status_code=403, detail=str(e))

        from sqlalchemy import select

        from .models import ApiKeyModel
        from .service import _hash_key

        key_hash = _hash_key(raw_key)
        result = await db.execute(
            select(ApiKeyModel).where(ApiKeyModel.key_hash == key_hash)
        )
        key_record = result.scalar_one()

        return KeyResponse(
            api_key=raw_key,
            key_id=key_record.id,
            project_code=key_record.project_code,
            created_at=key_record.created_at,
        )

    @router.get("/info", response_model=list[KeyInfo])
    async def key_info(
        request: Request, db: AsyncSession = Depends(db_dependency),
    ) -> list[KeyInfo]:
        """List keys for the authenticated project."""
        project_code = getattr(request.state, "project_code", None)
        if not project_code:
            raise HTTPException(status_code=401, detail="Authentication required.")

        keys = await service.get_project_keys(db, project_code)
        return [KeyInfo(**k) for k in keys]

    return router
