"""Tests for the built-in LogActionHandler."""

import pytest
from bloque_automation.handlers.log_handler import LogActionHandler
from bloque_automation.models.action import Action, ActionType


class TestLogActionHandler:
    @pytest.fixture
    def handler(self):
        return LogActionHandler()

    async def test_execute_returns_logged(self, handler):
        action = Action(action_type=ActionType.LOG, name="test")
        result = await handler.execute(action, {"key": "value"})
        assert result == {"status": "logged"}

    async def test_health_check_always_true(self, handler):
        assert await handler.health_check() is True
