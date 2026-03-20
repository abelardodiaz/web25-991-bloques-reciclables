"""Rule model combining conditions and actions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from bloque_automation.models.action import Action
from bloque_automation.models.condition import Condition


@dataclass
class Rule:
    """A rule that evaluates conditions and executes actions.

    Args:
        rule_id: Unique identifier.
        name: Human-readable name.
        conditions: Root condition node (tree).
        actions: Actions to execute when conditions match.
        enabled: Whether the rule is active.
        priority: Higher = evaluated first.
        stop_on_first_action_failure: If True, skip remaining actions after first failure.
        tenant_id: Optional tenant scope.
        metadata: Arbitrary metadata.
    """

    rule_id: str
    name: str
    conditions: Condition
    actions: list[Action] = field(default_factory=list)
    enabled: bool = True
    priority: int = 0
    stop_on_first_action_failure: bool = False
    tenant_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
