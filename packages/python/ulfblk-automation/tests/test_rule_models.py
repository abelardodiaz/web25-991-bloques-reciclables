"""Tests for rule models."""

from ulfblk_automation.models.action import Action, ActionType
from ulfblk_automation.models.condition import Condition, Operator
from ulfblk_automation.models.rule import Rule


class TestRule:
    def test_rule_defaults(self):
        cond = Condition(operator=Operator.EQ, field="x", value=1)
        rule = Rule(rule_id="r1", name="Test", conditions=cond)
        assert rule.rule_id == "r1"
        assert rule.enabled is True
        assert rule.priority == 0
        assert rule.stop_on_first_action_failure is False
        assert rule.tenant_id is None
        assert rule.actions == []
        assert rule.metadata == {}

    def test_rule_with_actions(self):
        cond = Condition(operator=Operator.EQ, field="x", value=1)
        actions = [Action(action_type=ActionType.LOG)]
        rule = Rule(rule_id="r2", name="With actions", conditions=cond, actions=actions)
        assert len(rule.actions) == 1

    def test_rule_tenant(self):
        cond = Condition(operator=Operator.EQ, field="x", value=1)
        rule = Rule(rule_id="r3", name="Tenant", conditions=cond, tenant_id="t1")
        assert rule.tenant_id == "t1"

    def test_rule_priority(self):
        cond = Condition(operator=Operator.EQ, field="x", value=1)
        rule = Rule(rule_id="r4", name="Priority", conditions=cond, priority=99)
        assert rule.priority == 99
