"""Checkout session data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class CheckoutMode(StrEnum):
    """Stripe checkout session modes."""

    PAYMENT = "payment"
    SUBSCRIPTION = "subscription"
    SETUP = "setup"


@dataclass
class CheckoutCreate:
    """Data for creating a Stripe checkout session.

    Args:
        customer_id: Stripe customer ID.
        price_id: Stripe price ID.
        success_url: URL to redirect on success.
        cancel_url: URL to redirect on cancel.
        mode: Checkout mode (payment, subscription, setup).
        metadata: Arbitrary key-value metadata.
    """

    customer_id: str
    price_id: str
    success_url: str
    cancel_url: str
    mode: CheckoutMode = CheckoutMode.SUBSCRIPTION
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class CheckoutData:
    """Stripe checkout session data returned from API.

    Args:
        id: Stripe checkout session ID (cs_xxx).
        url: Hosted checkout URL for redirection.
        status: Current session status.
    """

    id: str
    url: str
    status: str = ""
