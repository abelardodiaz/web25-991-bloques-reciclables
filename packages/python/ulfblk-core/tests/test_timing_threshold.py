"""Tests for TimingMiddleware configurable threshold."""

import asyncio
import logging

import pytest
from ulfblk_core.middleware.timing import TimingMiddleware
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


def _make_app(threshold: float | None = None):
    app = FastAPI()
    if threshold is not None:
        app.add_middleware(TimingMiddleware, slow_request_threshold=threshold)
    else:
        app.add_middleware(TimingMiddleware)

    @app.get("/fast")
    async def fast():
        return {"speed": "fast"}

    @app.get("/slow")
    async def slow():
        await asyncio.sleep(0.15)
        return {"speed": "slow"}

    return app


@pytest.mark.asyncio
async def test_default_threshold_no_warning(caplog):
    """Default threshold is 1.0s - a 150ms request should not warn."""
    app = _make_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with caplog.at_level(logging.WARNING):
            resp = await client.get("/slow")
    assert resp.status_code == 200
    assert not any("Slow request" in msg for msg in caplog.messages)


@pytest.mark.asyncio
async def test_custom_threshold_triggers_warning(caplog):
    """A low threshold should trigger a slow request warning."""
    app = _make_app(threshold=0.05)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with caplog.at_level(logging.WARNING):
            resp = await client.get("/slow")
    assert resp.status_code == 200
    assert any("Slow request" in msg for msg in caplog.messages)


@pytest.mark.asyncio
async def test_custom_threshold_no_warning(caplog):
    """A high threshold should not trigger a warning for a fast request."""
    app = _make_app(threshold=10.0)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with caplog.at_level(logging.WARNING):
            resp = await client.get("/fast")
    assert resp.status_code == 200
    assert not any("Slow request" in msg for msg in caplog.messages)
