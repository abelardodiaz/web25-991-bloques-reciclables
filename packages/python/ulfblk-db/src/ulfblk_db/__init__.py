"""ulfblk-db: Database infrastructure for the Bloques ecosystem."""

__version__ = "0.1.0"

from .config.settings import DatabaseSettings
from .engine.factory import create_async_engine
from .engine.health import db_health_check
from .models.base import Base
from .models.mixins import SoftDeleteMixin, TimestampMixin
from .session.dependency import get_db_session
from .session.factory import create_session_factory

__all__ = [
    "Base",
    "DatabaseSettings",
    "SoftDeleteMixin",
    "TimestampMixin",
    "create_async_engine",
    "create_session_factory",
    "db_health_check",
    "get_db_session",
]
