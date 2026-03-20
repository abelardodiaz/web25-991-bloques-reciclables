"""bloque-automation - Rule engine with composable condition evaluator."""

__version__ = "0.1.0"

from bloque_automation.evaluator.engine import evaluate_condition, resolve_field
from bloque_automation.handlers.log_handler import LogActionHandler
from bloque_automation.health.check import automation_health_check
from bloque_automation.models.action import Action, ActionType
from bloque_automation.models.condition import Condition, Operator
from bloque_automation.models.result import ActionResult, ActionStatus, RuleResult
from bloque_automation.models.rule import Rule
from bloque_automation.models.settings import RuleEngineSettings
from bloque_automation.protocol.handler import ActionHandler
from bloque_automation.service.rule_engine import RuleEngine

__all__ = [
    "Action",
    "ActionHandler",
    "ActionResult",
    "ActionStatus",
    "ActionType",
    "Condition",
    "LogActionHandler",
    "Operator",
    "Rule",
    "RuleEngine",
    "RuleEngineSettings",
    "RuleResult",
    "automation_health_check",
    "evaluate_condition",
    "resolve_field",
]
