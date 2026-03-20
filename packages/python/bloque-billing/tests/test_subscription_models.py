"""Tests for subscription data models."""

import pytest
from bloque_billing.models.subscription import (
    SubscriptionCreate,
    SubscriptionData,
    SubscriptionStatus,
)


class TestSubscriptionStatus:
    def test_values(self):
        assert SubscriptionStatus.ACTIVE == "active"
        assert SubscriptionStatus.PAST_DUE == "past_due"
        assert SubscriptionStatus.CANCELED == "canceled"
        assert SubscriptionStatus.TRIALING == "trialing"

    def test_from_string(self):
        status = SubscriptionStatus("active")
        assert status is SubscriptionStatus.ACTIVE


class TestSubscriptionCreate:
    def test_required_fields(self):
        s = SubscriptionCreate(customer_id="cus_123", price_id="price_456")
        assert s.customer_id == "cus_123"
        assert s.price_id == "price_456"
        assert s.trial_period_days is None

    def test_with_trial(self):
        s = SubscriptionCreate(
            customer_id="cus_123",
            price_id="price_456",
            trial_period_days=14,
            metadata={"source": "web"},
        )
        assert s.trial_period_days == 14
        assert s.metadata["source"] == "web"


class TestSubscriptionData:
    def test_frozen(self):
        s = SubscriptionData(
            id="sub_123",
            customer_id="cus_456",
            status=SubscriptionStatus.ACTIVE,
        )
        assert s.cancel_at_period_end is False
        with pytest.raises(AttributeError):
            s.id = "sub_999"  # type: ignore[misc]
