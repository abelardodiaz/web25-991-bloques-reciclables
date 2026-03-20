"""Webhook event data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class WebhookEventType(StrEnum):
    """Common Stripe webhook event types."""

    CHECKOUT_COMPLETED = "checkout.session.completed"
    CUSTOMER_CREATED = "customer.created"
    CUSTOMER_UPDATED = "customer.updated"
    CUSTOMER_DELETED = "customer.deleted"
    SUBSCRIPTION_CREATED = "customer.subscription.created"
    SUBSCRIPTION_UPDATED = "customer.subscription.updated"
    SUBSCRIPTION_DELETED = "customer.subscription.deleted"
    INVOICE_PAID = "invoice.paid"
    INVOICE_PAYMENT_FAILED = "invoice.payment_failed"


@dataclass(frozen=True)
class WebhookEvent:
    """Parsed Stripe webhook event.

    Args:
        id: Stripe event ID (evt_xxx).
        event_type: Event type string (any Stripe event, not limited to enum).
        data: Event data payload (typically the Stripe object).
        created: Unix timestamp of event creation.
    """

    id: str
    event_type: str
    data: dict[str, Any] = field(default_factory=dict)
    created: int = 0
