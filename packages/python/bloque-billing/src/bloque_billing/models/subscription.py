"""Subscription data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class SubscriptionStatus(StrEnum):
    """Stripe subscription statuses."""

    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    TRIALING = "trialing"
    UNPAID = "unpaid"
    PAUSED = "paused"


@dataclass
class SubscriptionCreate:
    """Data for creating a Stripe subscription.

    Args:
        customer_id: Stripe customer ID.
        price_id: Stripe price ID.
        metadata: Arbitrary key-value metadata.
        trial_period_days: Optional trial period in days.
    """

    customer_id: str
    price_id: str
    metadata: dict[str, str] = field(default_factory=dict)
    trial_period_days: int | None = None


@dataclass(frozen=True)
class SubscriptionData:
    """Stripe subscription data returned from API.

    Args:
        id: Stripe subscription ID (sub_xxx).
        customer_id: Associated customer ID.
        status: Current subscription status.
        price_id: Associated price ID.
        current_period_start: Unix timestamp of current period start.
        current_period_end: Unix timestamp of current period end.
        cancel_at_period_end: Whether subscription cancels at period end.
        metadata: Stripe metadata dict.
    """

    id: str
    customer_id: str
    status: SubscriptionStatus
    price_id: str = ""
    current_period_start: int = 0
    current_period_end: int = 0
    cancel_at_period_end: bool = False
    metadata: dict[str, str] = field(default_factory=dict)
