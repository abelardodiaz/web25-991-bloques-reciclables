"""Settings for the rule engine."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RuleEngineSettings:
    """Configuration for the RuleEngine.

    Args:
        tenant_aware: Enable multitenant isolation via bloque_multitenant context.
        max_rules: Maximum number of rules allowed (0 = unlimited).
        stop_on_rule_error: If True, stop evaluating rules after first error.
    """

    tenant_aware: bool = False
    max_rules: int = 0
    stop_on_rule_error: bool = False
