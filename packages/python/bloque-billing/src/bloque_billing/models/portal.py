"""Customer portal session data models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PortalCreate:
    """Data for creating a Stripe billing portal session.

    Args:
        customer_id: Stripe customer ID.
        return_url: URL to redirect when customer exits the portal.
    """

    customer_id: str
    return_url: str = ""


@dataclass(frozen=True)
class PortalData:
    """Stripe billing portal session data returned from API.

    Args:
        id: Stripe portal session ID (bps_xxx).
        url: Portal URL for redirection.
    """

    id: str
    url: str
