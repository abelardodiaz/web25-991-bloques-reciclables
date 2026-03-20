"""Tests for health check utility."""

from __future__ import annotations

from unittest.mock import AsyncMock

from bloque_notifications.health.check import notifications_health_check


async def test_all_healthy():
    providers = {
        "console": AsyncMock(health_check=AsyncMock(return_value=True)),
        "webhook": AsyncMock(health_check=AsyncMock(return_value=True)),
    }
    result = await notifications_health_check(providers)
    assert result == {"console": True, "webhook": True}


async def test_one_unhealthy():
    providers = {
        "console": AsyncMock(health_check=AsyncMock(return_value=True)),
        "webhook": AsyncMock(health_check=AsyncMock(side_effect=RuntimeError("down"))),
    }
    result = await notifications_health_check(providers)
    assert result["console"] is True
    assert result["webhook"] is False


async def test_provider_without_health_check():
    """Provider without health_check is assumed healthy."""

    class BareProvider:
        pass

    providers = {"bare": BareProvider()}
    result = await notifications_health_check(providers)
    assert result == {"bare": True}
