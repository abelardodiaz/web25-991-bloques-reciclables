"""ulfblk-automation - Rule engine with composable condition evaluator."""

__version__ = "0.1.0"

from ulfblk_automation.evaluator.engine import evaluate_condition, resolve_field
from ulfblk_automation.handlers.log_handler import LogActionHandler
from ulfblk_automation.health.check import automation_health_check
from ulfblk_automation.models.action import Action, ActionType
from ulfblk_automation.models.condition import Condition, Operator
from ulfblk_automation.models.result import ActionResult, ActionStatus, RuleResult
from ulfblk_automation.models.rule import Rule
from ulfblk_automation.models.settings import RuleEngineSettings
from ulfblk_automation.protocol.handler import ActionHandler
from ulfblk_automation.service.rule_engine import RuleEngine

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
