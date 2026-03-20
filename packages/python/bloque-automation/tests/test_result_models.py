"""Tests for result models."""

from bloque_automation.models.action import ActionType
from bloque_automation.models.result import ActionResult, ActionStatus, RuleResult


class TestActionResult:
    def test_action_result_success(self):
        result = ActionResult(
            action_type=ActionType.LOG,
            status=ActionStatus.SUCCESS,
            detail={"status": "logged"},
        )
        assert result.status == ActionStatus.SUCCESS
        assert result.error == ""

    def test_action_result_failed(self):
        result = ActionResult(
            action_type=ActionType.WEBHOOK,
            status=ActionStatus.FAILED,
            error="Connection refused",
        )
        assert result.status == ActionStatus.FAILED
        assert result.error == "Connection refused"


class TestRuleResult:
    def test_rule_result_matched(self):
        result = RuleResult(rule_id="r1", rule_name="Test", matched=True)
        assert result.matched is True
        assert result.actions == []
        assert result.error == ""
