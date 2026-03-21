"""Tests for condition models."""

from ulfblk_automation.models.condition import Condition, Operator


class TestOperator:
    def test_comparison_operators_exist(self):
        assert Operator.EQ == "eq"
        assert Operator.GT == "gt"
        assert Operator.IN == "in"
        assert Operator.REGEX == "regex"

    def test_logical_operators_exist(self):
        assert Operator.AND == "and"
        assert Operator.OR == "or"
        assert Operator.NOT == "not"


class TestCondition:
    def test_leaf_condition(self):
        cond = Condition(operator=Operator.EQ, field="status", value="active")
        assert cond.operator == Operator.EQ
        assert cond.field == "status"
        assert cond.value == "active"
        assert cond.children == []

    def test_branch_condition(self):
        child1 = Condition(operator=Operator.EQ, field="a", value=1)
        child2 = Condition(operator=Operator.GT, field="b", value=2)
        cond = Condition(operator=Operator.AND, children=[child1, child2])
        assert cond.operator == Operator.AND
        assert len(cond.children) == 2
        assert cond.field == ""
        assert cond.value is None
