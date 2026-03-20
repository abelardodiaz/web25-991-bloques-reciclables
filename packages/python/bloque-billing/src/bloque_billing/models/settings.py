"""Billing configuration settings."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BillingSettings:
    """Configuration for billing provider.

    Args:
        api_key: Stripe secret key (sk_test_... or sk_live_...).
        webhook_secret: Stripe webhook signing secret (whsec_...).
        api_base_url: Stripe API base URL.
        api_version: Stripe API version header.
        timeout: HTTP request timeout in seconds.
        tenant_aware: Enable automatic tenant injection from context.
    """

    api_key: str = ""
    webhook_secret: str = ""
    api_base_url: str = "https://api.stripe.com"
    api_version: str = "2024-12-18.acacia"
    timeout: float = 30.0
    tenant_aware: bool = False
