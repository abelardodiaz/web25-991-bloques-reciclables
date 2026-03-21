"""Condition evaluation engine - sync, pure functions."""

from __future__ import annotations

import re
from typing import Any

from ulfblk_automation.models.condition import Condition, Operator

_LOGICAL_OPERATORS = frozenset({Operator.AND, Operator.OR, Operator.NOT})


def resolve_field(context: dict[str, Any], field_path: str) -> Any:
    """Resolve a dot-path in a nested dict.

    Args:
        context: The data dict to traverse.
        field_path: Dot-separated path (e.g. "user.plan.tier").

    Returns:
        The value at the path.

    Raises:
        KeyError: If any part of the path is missing.
    """
    current = context
    for part in field_path.split("."):
        if not isinstance(current, dict):
            raise KeyError(part)
        current = current[part]
    return current


def evaluate_condition(condition: Condition, context: dict[str, Any]) -> bool:
    """Evaluate a condition tree against a context dict.

    Logical operators (AND, OR, NOT) recurse into children.
    Comparison operators resolve the field and compare against value.
    Missing fields return False (no crash).

    Args:
        condition: Root condition node.
        context: Event data to evaluate against.

    Returns:
        True if the condition matches, False otherwise.
    """
    if condition.operator in _LOGICAL_OPERATORS:
        return _evaluate_logical(condition, context)
    return _evaluate_comparison(condition, context)


def _evaluate_logical(condition: Condition, context: dict[str, Any]) -> bool:
    """Evaluate logical operators (AND, OR, NOT)."""
    op = condition.operator

    if op == Operator.AND:
        return all(evaluate_condition(c, context) for c in condition.children)

    if op == Operator.OR:
        return any(evaluate_condition(c, context) for c in condition.children)

    if op == Operator.NOT:
        if not condition.children:
            return False
        return not evaluate_condition(condition.children[0], context)

    return False


def _evaluate_comparison(condition: Condition, context: dict[str, Any]) -> bool:
    """Evaluate comparison operators. Missing field -> False."""
    try:
        field_value = resolve_field(context, condition.field)
    except (KeyError, TypeError):
        return False

    op = condition.operator
    expected = condition.value

    try:
        if op == Operator.EQ:
            return field_value == expected
        if op == Operator.NEQ:
            return field_value != expected
        if op == Operator.GT:
            return field_value > expected
        if op == Operator.GTE:
            return field_value >= expected
        if op == Operator.LT:
            return field_value < expected
        if op == Operator.LTE:
            return field_value <= expected
        if op == Operator.IN:
            return field_value in expected
        if op == Operator.NOT_IN:
            return field_value not in expected
        if op == Operator.CONTAINS:
            return expected in field_value
        if op == Operator.STARTS_WITH:
            return str(field_value).startswith(str(expected))
        if op == Operator.ENDS_WITH:
            return str(field_value).endswith(str(expected))
        if op == Operator.REGEX:
            return bool(re.search(str(expected), str(field_value)))
    except (TypeError, ValueError):
        return False

    return False
