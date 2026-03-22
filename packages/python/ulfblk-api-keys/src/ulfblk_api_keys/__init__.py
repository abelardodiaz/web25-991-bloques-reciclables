"""ulfblk-api-keys: API key authentication for FastAPI services."""

__version__ = "0.1.0"

from .cache import InMemoryCache
from .config import ApiKeyConfig
from .middleware import ApiKeyAuth
from .models import ApiKeyModel, KeyAuditLog
from .router import create_api_keys_router
from .schemas import KeyInfo, KeyResponse, RegisterRequest, RotateRequest
from .service import ApiKeyService

__all__ = [
    "ApiKeyAuth",
    "ApiKeyConfig",
    "ApiKeyModel",
    "ApiKeyService",
    "InMemoryCache",
    "KeyAuditLog",
    "KeyInfo",
    "KeyResponse",
    "RegisterRequest",
    "RotateRequest",
    "create_api_keys_router",
]
