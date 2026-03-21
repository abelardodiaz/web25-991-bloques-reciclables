"""Result models for rule evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from ulfblk_automation.models.action import ActionType


class ActionStatus(StrEnum):
    """Outcome of an action execution."""

    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class ActionResult:
    """Result of a single action execution.

    Args:
        action_type: The type of action that was executed.
        status: Outcome status.
        detail: Handler-returned data on success.
        error: Error message on failure.
    """

    action_type: ActionType
    status: ActionStatus
    detail: dict[str, Any] = field(default_factory=dict)
    error: str = ""


@dataclass(frozen=True)
class RuleResult:
    """Result of evaluating a single rule against an event.

    Args:
        rule_id: The rule that was evaluated.
        rule_name: Human-readable rule name.
        matched: Whether conditions matched.
        actions: Results of action executions (empty if not matched).
        error: Error message if evaluation itself failed.
    """

    rule_id: str
    rule_name: str
    matched: bool
    actions: list[ActionResult] = field(default_factory=list)
    error: str = ""
