"""pytest plugin for bloque-testing.

Auto-registers fixtures when bloque-testing is installed.
Fixtures are conditionally available based on installed optional deps.

Registered via entry_points in pyproject.toml:
    [project.entry-points."pytest11"]
    bloque_testing = "bloque_testing.plugin"
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI

from .client import create_test_client


# -- Always-available fixtures (base deps) --


@pytest.fixture
def test_app() -> FastAPI:
    """A minimal FastAPI app with a /ping endpoint for testing."""
    app = FastAPI()

    @app.get("/ping")
    async def ping():
        return {"message": "pong"}

    return app


@pytest.fixture
async def test_client(test_app: FastAPI):
    """Async HTTP client bound to test_app."""
    async with create_test_client(test_app) as client:
        yield client


# -- Auth fixtures (requires [auth] optional deps) --

try:
    from .auth import create_jwt_manager, generate_rsa_keys

    @pytest.fixture(scope="session")
    def rsa_keys() -> tuple[str, str]:
        """RSA key pair for JWT testing. Session-scoped for performance."""
        return generate_rsa_keys()

    @pytest.fixture
    def jwt_manager(rsa_keys):
        """JWTManager with test RSA keys."""
        private_pem, public_pem = rsa_keys
        return create_jwt_manager(private_pem=private_pem, public_pem=public_pem)

except ImportError:
    pass


# -- DB fixtures (requires [db] optional deps) --

try:
    from .db import create_test_engine, create_test_session_factory

    @pytest.fixture
    def test_engine():
        """SQLite in-memory async engine."""
        return create_test_engine()

    @pytest.fixture
    def test_session_factory(test_engine):
        """Session factory bound to in-memory engine."""
        return create_test_session_factory(test_engine)

except ImportError:
    pass
