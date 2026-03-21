"""Tests for checkout data models."""

import pytest
from ulfblk_billing.models.checkout import (
    CheckoutCreate,
    CheckoutData,
    CheckoutMode,
)


class TestCheckoutMode:
    def test_values(self):
        assert CheckoutMode.PAYMENT == "payment"
        assert CheckoutMode.SUBSCRIPTION == "subscription"
        assert CheckoutMode.SETUP == "setup"


class TestCheckoutCreate:
    def test_defaults(self):
        c = CheckoutCreate(
            customer_id="cus_123",
            price_id="price_456",
            success_url="https://example.com/ok",
            cancel_url="https://example.com/cancel",
        )
        assert c.mode == CheckoutMode.SUBSCRIPTION
        assert c.metadata == {}

    def test_payment_mode(self):
        c = CheckoutCreate(
            customer_id="cus_123",
            price_id="price_456",
            success_url="https://example.com/ok",
            cancel_url="https://example.com/cancel",
            mode=CheckoutMode.PAYMENT,
        )
        assert c.mode == CheckoutMode.PAYMENT


class TestCheckoutData:
    def test_frozen(self):
        c = CheckoutData(id="cs_123", url="https://checkout.stripe.com/xxx")
        assert c.status == ""
        with pytest.raises(AttributeError):
            c.id = "cs_999"  # type: ignore[misc]
