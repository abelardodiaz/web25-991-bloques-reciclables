"""Condition model for rule evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as dataclass_field
from enum import StrEnum
from typing import Any


class Operator(StrEnum):
    """Operators for condition evaluation.

    Comparison operators work on leaf nodes (field + value).
    Logical operators work on branch nodes (children).
    """

    # Comparison
    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    REGEX = "regex"

    # Logical
    AND = "and"
    OR = "or"
    NOT = "not"


@dataclass
class Condition:
    """A single node in a condition tree.

    Leaf node (comparison): field + operator + value.
    Branch node (logical): operator + children.

    Example:
        # Leaf: user.age >= 18
        Condition(operator=Operator.GTE, field="user.age", value=18)

        # Branch: age >= 18 AND plan == "premium"
        Condition(
            operator=Operator.AND,
            children=[
                Condition(operator=Operator.GTE, field="user.age", value=18),
                Condition(operator=Operator.EQ, field="user.plan", value="premium"),
            ],
        )
    """

    operator: Operator
    field: str = ""
    value: Any = None
    children: list[Condition] = dataclass_field(default_factory=list)
