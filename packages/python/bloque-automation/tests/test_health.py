"""Tests for health check."""

from unittest.mock import AsyncMock

from bloque_automation.health.check import automation_health_check


class TestAutomationHealthCheck:
    async def test_all_healthy(self):
        handlers = {
            "log": AsyncMock(health_check=AsyncMock(return_value=True)),
            "webhook": AsyncMock(health_check=AsyncMock(return_value=True)),
        }
        result = await automation_health_check(handlers)
        assert result == {"log": True, "webhook": True}

    async def test_one_unhealthy(self):
        handlers = {
            "log": AsyncMock(health_check=AsyncMock(return_value=True)),
            "webhook": AsyncMock(health_check=AsyncMock(return_value=False)),
        }
        result = await automation_health_check(handlers)
        assert result["log"] is True
        assert result["webhook"] is False

    async def test_handler_exception_returns_false(self):
        handlers = {
            "broken": AsyncMock(health_check=AsyncMock(side_effect=RuntimeError("boom"))),
        }
        result = await automation_health_check(handlers)
        assert result["broken"] is False
