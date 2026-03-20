"""Tests for action models."""

from bloque_automation.models.action import Action, ActionType


class TestActionType:
    def test_action_types_exist(self):
        assert ActionType.NOTIFY == "notify"
        assert ActionType.WEBHOOK == "webhook"
        assert ActionType.LOG == "log"
        assert ActionType.CUSTOM == "custom"


class TestAction:
    def test_action_defaults(self):
        action = Action(action_type=ActionType.LOG)
        assert action.action_type == ActionType.LOG
        assert action.config == {}
        assert action.name == ""

    def test_action_with_config(self):
        action = Action(
            action_type=ActionType.WEBHOOK,
            config={"url": "https://example.com/hook"},
            name="my-webhook",
        )
        assert action.config["url"] == "https://example.com/hook"
        assert action.name == "my-webhook"
