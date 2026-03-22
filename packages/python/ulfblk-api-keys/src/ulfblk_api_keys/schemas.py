"""Pydantic schemas for API key operations."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class RegisterRequest(BaseModel):
    """Request to register a new API key."""

    project_code: str
    project_name: str
    secret: str


class RotateRequest(BaseModel):
    """Request to rotate an existing API key."""

    project_code: str
    old_api_key: str
    secret: str


class RevokeRequest(BaseModel):
    """Request to revoke an API key."""

    key_id: int
    secret: str


class KeyResponse(BaseModel):
    """Response after registering or rotating a key."""

    api_key: str
    key_id: int
    project_code: str
    created_at: datetime
    expires_at: datetime | None = None


class KeyInfo(BaseModel):
    """Info about an existing key (no raw key exposed)."""

    id: int
    project_code: str
    project_name: str
    is_active: bool
    request_count: int
    last_used_at: datetime | None = None
    created_at: datetime
    expires_at: datetime | None = None
