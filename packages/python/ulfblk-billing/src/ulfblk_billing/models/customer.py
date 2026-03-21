"""Customer data models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CustomerCreate:
    """Data for creating a Stripe customer.

    Args:
        email: Customer email address.
        name: Customer display name.
        metadata: Arbitrary key-value metadata.
        tenant_id: Injected into metadata by BillingService when tenant_aware.
    """

    email: str
    name: str = ""
    metadata: dict[str, str] = field(default_factory=dict)
    tenant_id: str | None = None


@dataclass(frozen=True)
class CustomerData:
    """Stripe customer data returned from API.

    Args:
        id: Stripe customer ID (cus_xxx).
        email: Customer email.
        name: Customer name.
        metadata: Stripe metadata dict.
        created: Unix timestamp of creation.
    """

    id: str
    email: str
    name: str = ""
    metadata: dict[str, str] = field(default_factory=dict)
    created: int = 0
