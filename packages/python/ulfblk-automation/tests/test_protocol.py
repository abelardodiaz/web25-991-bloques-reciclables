"""Tests for the ActionHandler protocol."""

from ulfblk_automation.handlers.log_handler import LogActionHandler
from ulfblk_automation.protocol.handler import ActionHandler


class TestActionHandlerProtocol:
    def test_log_handler_satisfies_protocol(self):
        handler = LogActionHandler()
        assert isinstance(handler, ActionHandler)

    def test_duck_typed_handler_satisfies_protocol(self):
        class CustomHandler:
            async def execute(self, action, context):
                return {}

            async def health_check(self):
                return True

        assert isinstance(CustomHandler(), ActionHandler)

    def test_incomplete_handler_fails_protocol(self):
        class BadHandler:
            async def execute(self, action, context):
                return {}

        assert not isinstance(BadHandler(), ActionHandler)
