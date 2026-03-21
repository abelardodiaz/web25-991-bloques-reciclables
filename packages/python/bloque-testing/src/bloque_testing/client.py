"""HTTP test client factories for FastAPI applications."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


@asynccontextmanager
async def create_test_client(
    app: FastAPI,
    base_url: str = "http://test",
    **client_kwargs: Any,
) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP test client for a FastAPI app.

    Args:
        app: FastAPI application instance.
        base_url: Base URL for requests.
        **client_kwargs: Additional kwargs passed to AsyncClient.

    Yields:
        Configured AsyncClient bound to the app via ASGITransport.

    Example::

        async with create_test_client(app) as client:
            resp = await client.get("/health")
            assert resp.status_code == 200
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url=base_url, **client_kwargs
    ) as client:
        yield client


@asynccontextmanager
async def create_authenticated_client(
    app: FastAPI,
    token: str,
    base_url: str = "http://test",
    **client_kwargs: Any,
) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with JWT Bearer authentication pre-configured.

    Args:
        app: FastAPI application instance.
        token: JWT token string (access token).
        base_url: Base URL for requests.
        **client_kwargs: Additional kwargs passed to AsyncClient.

    Yields:
        AsyncClient with Authorization header set.

    Example::

        token = create_test_token(jwt_manager, user_id="u-1")
        async with create_authenticated_client(app, token) as client:
            resp = await client.get("/protected")
            assert resp.status_code == 200
    """
    transport = ASGITransport(app=app)
    headers = dict(client_kwargs.pop("headers", {}))
    headers["Authorization"] = f"Bearer {token}"
    async with AsyncClient(
        transport=transport,
        base_url=base_url,
        headers=headers,
        **client_kwargs,
    ) as client:
        yield client
