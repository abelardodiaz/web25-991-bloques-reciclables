"""Tests for the condition evaluator - MOST CRITICAL."""

import pytest
from bloque_automation.evaluator.engine import evaluate_condition, resolve_field
from bloque_automation.models.condition import Condition, Operator


class TestResolveField:
    def test_simple_field(self):
        assert resolve_field({"status": "active"}, "status") == "active"

    def test_nested_field(self):
        ctx = {"user": {"plan": {"tier": "premium"}}}
        assert resolve_field(ctx, "user.plan.tier") == "premium"

    def test_missing_field_raises(self):
        with pytest.raises(KeyError):
            resolve_field({"a": 1}, "b")

    def test_missing_nested_field_raises(self):
        with pytest.raises(KeyError):
            resolve_field({"user": {"name": "x"}}, "user.plan.tier")


class TestEvaluateComparison:
    def test_eq_true(self):
        cond = Condition(operator=Operator.EQ, field="status", value="active")
        assert evaluate_condition(cond, {"status": "active"}) is True

    def test_eq_false(self):
        cond = Condition(operator=Operator.EQ, field="status", value="active")
        assert evaluate_condition(cond, {"status": "inactive"}) is False

    def test_neq(self):
        cond = Condition(operator=Operator.NEQ, field="status", value="active")
        assert evaluate_condition(cond, {"status": "inactive"}) is True

    def test_gt(self):
        cond = Condition(operator=Operator.GT, field="age", value=18)
        assert evaluate_condition(cond, {"age": 25}) is True
        assert evaluate_condition(cond, {"age": 18}) is False

    def test_gte(self):
        cond = Condition(operator=Operator.GTE, field="age", value=18)
        assert evaluate_condition(cond, {"age": 18}) is True
        assert evaluate_condition(cond, {"age": 17}) is False

    def test_lt(self):
        cond = Condition(operator=Operator.LT, field="age", value=18)
        assert evaluate_condition(cond, {"age": 10}) is True

    def test_lte(self):
        cond = Condition(operator=Operator.LTE, field="age", value=18)
        assert evaluate_condition(cond, {"age": 18}) is True

    def test_in(self):
        cond = Condition(operator=Operator.IN, field="role", value=["admin", "editor"])
        assert evaluate_condition(cond, {"role": "admin"}) is True
        assert evaluate_condition(cond, {"role": "viewer"}) is False

    def test_not_in(self):
        cond = Condition(operator=Operator.NOT_IN, field="role", value=["banned"])
        assert evaluate_condition(cond, {"role": "admin"}) is True
        assert evaluate_condition(cond, {"role": "banned"}) is False

    def test_contains(self):
        cond = Condition(operator=Operator.CONTAINS, field="email", value="@example")
        assert evaluate_condition(cond, {"email": "user@example.com"}) is True

    def test_starts_with(self):
        cond = Condition(operator=Operator.STARTS_WITH, field="name", value="John")
        assert evaluate_condition(cond, {"name": "John Doe"}) is True
        assert evaluate_condition(cond, {"name": "Jane Doe"}) is False

    def test_ends_with(self):
        cond = Condition(operator=Operator.ENDS_WITH, field="file", value=".pdf")
        assert evaluate_condition(cond, {"file": "report.pdf"}) is True

    def test_regex(self):
        cond = Condition(operator=Operator.REGEX, field="code", value=r"^[A-Z]{3}-\d+$")
        assert evaluate_condition(cond, {"code": "ABC-123"}) is True
        assert evaluate_condition(cond, {"code": "abc-123"}) is False


class TestEvaluateLogical:
    def test_and_all_true(self):
        cond = Condition(
            operator=Operator.AND,
            children=[
                Condition(operator=Operator.EQ, field="a", value=1),
                Condition(operator=Operator.EQ, field="b", value=2),
            ],
        )
        assert evaluate_condition(cond, {"a": 1, "b": 2}) is True

    def test_and_one_false(self):
        cond = Condition(
            operator=Operator.AND,
            children=[
                Condition(operator=Operator.EQ, field="a", value=1),
                Condition(operator=Operator.EQ, field="b", value=99),
            ],
        )
        assert evaluate_condition(cond, {"a": 1, "b": 2}) is False

    def test_or_one_true(self):
        cond = Condition(
            operator=Operator.OR,
            children=[
                Condition(operator=Operator.EQ, field="role", value="admin"),
                Condition(operator=Operator.EQ, field="role", value="editor"),
            ],
        )
        assert evaluate_condition(cond, {"role": "editor"}) is True

    def test_or_none_true(self):
        cond = Condition(
            operator=Operator.OR,
            children=[
                Condition(operator=Operator.EQ, field="role", value="admin"),
                Condition(operator=Operator.EQ, field="role", value="editor"),
            ],
        )
        assert evaluate_condition(cond, {"role": "viewer"}) is False

    def test_not_inverts(self):
        cond = Condition(
            operator=Operator.NOT,
            children=[
                Condition(operator=Operator.EQ, field="banned", value=True),
            ],
        )
        assert evaluate_condition(cond, {"banned": False}) is True
        assert evaluate_condition(cond, {"banned": True}) is False

    def test_not_empty_children(self):
        cond = Condition(operator=Operator.NOT, children=[])
        assert evaluate_condition(cond, {}) is False


class TestEvaluateMissingField:
    def test_missing_field_returns_false(self):
        cond = Condition(operator=Operator.EQ, field="nonexistent", value="x")
        assert evaluate_condition(cond, {"other": "y"}) is False

    def test_missing_nested_field_returns_false(self):
        cond = Condition(operator=Operator.EQ, field="user.plan.tier", value="premium")
        assert evaluate_condition(cond, {"user": {"name": "x"}}) is False


class TestNestedFieldAccess:
    def test_deeply_nested(self):
        cond = Condition(operator=Operator.EQ, field="a.b.c.d", value=42)
        ctx = {"a": {"b": {"c": {"d": 42}}}}
        assert evaluate_condition(cond, ctx) is True
