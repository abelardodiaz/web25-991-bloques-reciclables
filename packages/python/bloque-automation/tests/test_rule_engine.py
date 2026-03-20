"""Tests for the RuleEngine orchestrator."""

import pytest
from bloque_automation.models.action import Action, ActionType
from bloque_automation.models.condition import Condition, Operator
from bloque_automation.models.result import ActionStatus
from bloque_automation.models.rule import Rule
from bloque_automation.models.settings import RuleEngineSettings
from bloque_automation.service.rule_engine import RuleEngine


class TestRuleEngineBasic:
    async def test_evaluate_matching_rule(self, engine, simple_rule, log_handler):
        engine.register_handler(ActionType.LOG, log_handler)
        engine.add_rule(simple_rule)
        results = await engine.evaluate({"status": "active"})
        assert len(results) == 1
        assert results[0].matched is True
        assert results[0].actions[0].status == ActionStatus.SUCCESS

    async def test_evaluate_non_matching_rule(self, engine, simple_rule, log_handler):
        engine.register_handler(ActionType.LOG, log_handler)
        engine.add_rule(simple_rule)
        results = await engine.evaluate({"status": "inactive"})
        assert len(results) == 1
        assert results[0].matched is False
        assert results[0].actions == []

    async def test_no_handler_returns_skipped(self, engine, simple_rule):
        engine.add_rule(simple_rule)
        results = await engine.evaluate({"status": "active"})
        assert results[0].matched is True
        assert results[0].actions[0].status == ActionStatus.SKIPPED

    async def test_priority_order(self, engine, log_handler):
        engine.register_handler(ActionType.LOG, log_handler)
        low = Rule(
            rule_id="low",
            name="Low",
            conditions=Condition(operator=Operator.EQ, field="x", value=1),
            actions=[Action(action_type=ActionType.LOG)],
            priority=1,
        )
        high = Rule(
            rule_id="high",
            name="High",
            conditions=Condition(operator=Operator.EQ, field="x", value=1),
            actions=[Action(action_type=ActionType.LOG)],
            priority=10,
        )
        engine.add_rule(low)
        engine.add_rule(high)
        results = await engine.evaluate({"x": 1})
        assert results[0].rule_id == "high"
        assert results[1].rule_id == "low"


class TestRuleEngineTenant:
    async def test_tenant_isolation(self, engine, log_handler):
        engine.register_handler(ActionType.LOG, log_handler)
        cond = Condition(operator=Operator.EQ, field="x", value=1)
        rule_a = Rule(rule_id="a", name="A", conditions=cond,
                      actions=[Action(action_type=ActionType.LOG)], tenant_id="tenant-a")
        rule_b = Rule(rule_id="b", name="B", conditions=cond,
                      actions=[Action(action_type=ActionType.LOG)], tenant_id="tenant-b")
        engine.add_rule(rule_a)
        engine.add_rule(rule_b)
        results = await engine.evaluate({"x": 1}, tenant_id="tenant-a")
        rule_ids = [r.rule_id for r in results]
        assert "a" in rule_ids
        assert "b" not in rule_ids


class TestRuleEngineFailure:
    async def test_action_failure_returns_failed(self, engine, simple_rule, mock_failing_handler):
        engine.register_handler(ActionType.LOG, mock_failing_handler)
        engine.add_rule(simple_rule)
        results = await engine.evaluate({"status": "active"})
        assert results[0].matched is True
        assert results[0].actions[0].status == ActionStatus.FAILED
        assert "Handler down" in results[0].actions[0].error

    async def test_stop_on_first_action_failure(self, engine, mock_failing_handler, log_handler):
        engine.register_handler(ActionType.LOG, mock_failing_handler)
        engine.register_handler(ActionType.NOTIFY, log_handler)
        cond = Condition(operator=Operator.EQ, field="x", value=1)
        rule = Rule(
            rule_id="stop-rule",
            name="Stop Rule",
            conditions=cond,
            actions=[
                Action(action_type=ActionType.LOG, name="will-fail"),
                Action(action_type=ActionType.NOTIFY, name="should-skip"),
            ],
            stop_on_first_action_failure=True,
        )
        engine.add_rule(rule)
        results = await engine.evaluate({"x": 1})
        assert results[0].actions[0].status == ActionStatus.FAILED
        assert results[0].actions[1].status == ActionStatus.SKIPPED


class TestRuleEngineManagement:
    def test_add_and_remove_rule(self, engine, simple_rule):
        engine.add_rule(simple_rule)
        assert len(engine.get_rules(enabled_only=False)) == 1
        assert engine.remove_rule(simple_rule.rule_id) is True
        assert len(engine.get_rules(enabled_only=False)) == 0

    def test_remove_nonexistent_returns_false(self, engine):
        assert engine.remove_rule("nope") is False

    def test_max_rules_limit(self):
        engine = RuleEngine(settings=RuleEngineSettings(max_rules=1))
        cond = Condition(operator=Operator.EQ, field="x", value=1)
        engine.add_rule(Rule(rule_id="r1", name="R1", conditions=cond))
        with pytest.raises(ValueError, match="Max rules limit"):
            engine.add_rule(Rule(rule_id="r2", name="R2", conditions=cond))

    async def test_disabled_rule_skipped(self, engine, log_handler):
        engine.register_handler(ActionType.LOG, log_handler)
        cond = Condition(operator=Operator.EQ, field="x", value=1)
        rule = Rule(
            rule_id="disabled",
            name="Disabled",
            conditions=cond,
            actions=[Action(action_type=ActionType.LOG)],
            enabled=False,
        )
        engine.add_rule(rule)
        results = await engine.evaluate({"x": 1})
        assert len(results) == 0
