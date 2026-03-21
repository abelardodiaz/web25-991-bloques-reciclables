"""bloque-testing: Shared testing utilities for the Bloques ecosystem."""

__version__ = "0.1.0"

from .client import create_authenticated_client, create_test_client
from .settings import create_test_settings, override_settings

__all__ = [
    "create_authenticated_client",
    "create_test_client",
    "create_test_settings",
    "override_settings",
]


def __getattr__(name: str):
    if name in ("generate_rsa_keys", "create_jwt_manager", "create_test_token"):
        from . import auth

        return getattr(auth, name)
    if name in (
        "create_test_engine",
        "create_test_session_factory",
        "create_tables",
        "drop_tables",
    ):
        from . import db

        return getattr(db, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
