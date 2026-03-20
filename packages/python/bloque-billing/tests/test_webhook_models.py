"""Tests for webhook data models."""

import pytest
from bloque_billing.models.webhook import WebhookEvent, WebhookEventType


class TestWebhookEventType:
    def test_checkout_completed(self):
        assert WebhookEventType.CHECKOUT_COMPLETED == "checkout.session.completed"

    def test_subscription_events(self):
        assert WebhookEventType.SUBSCRIPTION_CREATED == "customer.subscription.created"
        assert WebhookEventType.SUBSCRIPTION_DELETED == "customer.subscription.deleted"

    def test_from_string(self):
        et = WebhookEventType("invoice.paid")
        assert et is WebhookEventType.INVOICE_PAID


class TestWebhookEvent:
    def test_minimal(self):
        e = WebhookEvent(id="evt_123", event_type="customer.created")
        assert e.data == {}
        assert e.created == 0

    def test_frozen(self):
        e = WebhookEvent(
            id="evt_123",
            event_type="customer.created",
            data={"id": "cus_456"},
            created=1700000000,
        )
        with pytest.raises(AttributeError):
            e.id = "evt_999"  # type: ignore[misc]
