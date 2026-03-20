"""Shared fixtures for bloque-automation tests."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from bloque_automation.handlers.log_handler import LogActionHandler
from bloque_automation.models.action import Action, ActionType
from bloque_automation.models.condition import Condition, Operator
from bloque_automation.models.rule import Rule
from bloque_automation.models.settings import RuleEngineSettings
from bloque_automation.service.rule_engine import RuleEngine


@pytest.fixture
def simple_condition():
    """A simple equality condition: status == 'active'."""
    return Condition(operator=Operator.EQ, field="status", value="active")


@pytest.fixture
def nested_condition():
    """AND condition: status == 'active' AND user.age >= 18."""
    return Condition(
        operator=Operator.AND,
        children=[
            Condition(operator=Operator.EQ, field="status", value="active"),
            Condition(operator=Operator.GTE, field="user.age", value=18),
        ],
    )


@pytest.fixture
def log_action():
    return Action(action_type=ActionType.LOG, name="test-log")


@pytest.fixture
def notify_action():
    return Action(
        action_type=ActionType.NOTIFY,
        name="test-notify",
        config={"recipient": "admin@example.com"},
    )


@pytest.fixture
def simple_rule(simple_condition, log_action):
    return Rule(
        rule_id="rule-1",
        name="Simple Rule",
        conditions=simple_condition,
        actions=[log_action],
    )


@pytest.fixture
def priority_rule(nested_condition, log_action):
    return Rule(
        rule_id="rule-2",
        name="Priority Rule",
        conditions=nested_condition,
        actions=[log_action],
        priority=10,
    )


@pytest.fixture
def tenant_rule(simple_condition, log_action):
    return Rule(
        rule_id="rule-tenant",
        name="Tenant Rule",
        conditions=simple_condition,
        actions=[log_action],
        tenant_id="tenant-a",
    )


@pytest.fixture
def log_handler():
    return LogActionHandler()


@pytest.fixture
def mock_handler():
    """A mock handler that satisfies ActionHandler protocol."""
    handler = AsyncMock()
    handler.execute = AsyncMock(return_value={"status": "done"})
    handler.health_check = AsyncMock(return_value=True)
    return handler


@pytest.fixture
def mock_failing_handler():
    """A mock handler that always fails on execute."""
    handler = AsyncMock()
    handler.execute = AsyncMock(side_effect=RuntimeError("Handler down"))
    handler.health_check = AsyncMock(return_value=False)
    return handler


@pytest.fixture
def engine_settings():
    return RuleEngineSettings()


@pytest.fixture
def engine(engine_settings):
    return RuleEngine(settings=engine_settings)
