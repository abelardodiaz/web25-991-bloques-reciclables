"""Stripe billing provider using httpx with form-encoded requests."""

from __future__ import annotations

from typing import Any

import httpx

from ulfblk_billing.models.checkout import CheckoutCreate, CheckoutData
from ulfblk_billing.models.customer import CustomerCreate, CustomerData
from ulfblk_billing.models.portal import PortalCreate, PortalData
from ulfblk_billing.models.settings import BillingSettings
from ulfblk_billing.models.subscription import (
    SubscriptionCreate,
    SubscriptionData,
    SubscriptionStatus,
)


class StripeProvider:
    """Stripe billing provider using httpx (no Stripe SDK).

    Uses form-encoded bodies (application/x-www-form-urlencoded) as
    required by the Stripe REST API.

    Example:
        provider = StripeProvider(settings)
        async with provider:
            customer = await provider.create_customer(
                CustomerCreate(email="user@example.com")
            )
    """

    def __init__(
        self,
        settings: BillingSettings,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings
        self._external_client = http_client is not None
        self._client = http_client

    async def start(self) -> None:
        """Create the httpx.AsyncClient if not provided externally."""
        if self._client is not None:
            return
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.settings.timeout, connect=10.0),
        )

    async def stop(self) -> None:
        """Close the httpx.AsyncClient if we own it."""
        if self._client is not None and not self._external_client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the httpx client. Raises RuntimeError if not started."""
        if self._client is None:
            raise RuntimeError(
                "StripeProvider is not started. Call start() or use async with."
            )
        return self._client

    # -- Internal helpers --

    def _headers(self) -> dict[str, str]:
        """Build common request headers."""
        return {
            "Authorization": f"Bearer {self.settings.api_key}",
            "Stripe-Version": self.settings.api_version,
        }

    async def _request(
        self,
        method: str,
        path: str,
        *,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a form-encoded request to the Stripe API.

        Args:
            method: HTTP method (GET, POST, DELETE).
            path: API path (e.g. /v1/customers).
            data: Parameters to send as form-encoded body.

        Returns:
            Parsed JSON response.

        Raises:
            httpx.HTTPStatusError: On non-2xx response.
        """
        url = f"{self.settings.api_base_url}{path}"
        flat = self._flatten_params(data) if data else None

        response = await self.client.request(
            method,
            url,
            headers=self._headers(),
            data=flat,
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _flatten_params(
        params: dict[str, Any], prefix: str = ""
    ) -> dict[str, str]:
        """Flatten nested dict to Stripe form-encoded format.

        Converts nested structures like:
            {"metadata": {"tenant_id": "abc"}, "items": [{"price": "x"}]}
        To:
            {"metadata[tenant_id]": "abc", "items[0][price]": "x"}
        """
        result: dict[str, str] = {}
        for key, value in params.items():
            full_key = f"{prefix}[{key}]" if prefix else key

            if isinstance(value, dict):
                result.update(StripeProvider._flatten_params(value, full_key))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    item_key = f"{full_key}[{i}]"
                    if isinstance(item, dict):
                        result.update(
                            StripeProvider._flatten_params(item, item_key)
                        )
                    else:
                        result[item_key] = str(item)
            elif isinstance(value, bool):
                result[full_key] = "true" if value else "false"
            elif value is not None:
                result[full_key] = str(value)

        return result

    @staticmethod
    def _parse_customer(data: dict[str, Any]) -> CustomerData:
        """Parse Stripe customer API response to CustomerData."""
        return CustomerData(
            id=data["id"],
            email=data.get("email", ""),
            name=data.get("name", "") or "",
            metadata=dict(data.get("metadata", {})),
            created=data.get("created", 0),
        )

    @staticmethod
    def _parse_subscription(data: dict[str, Any]) -> SubscriptionData:
        """Parse Stripe subscription API response to SubscriptionData."""
        # Extract price_id from items
        price_id = ""
        items = data.get("items", {})
        if isinstance(items, dict):
            item_data = items.get("data", [])
            if item_data and isinstance(item_data, list):
                first_item = item_data[0]
                price = first_item.get("price", {})
                if isinstance(price, dict):
                    price_id = price.get("id", "")

        return SubscriptionData(
            id=data["id"],
            customer_id=data.get("customer", ""),
            status=SubscriptionStatus(data.get("status", "active")),
            price_id=price_id,
            current_period_start=data.get("current_period_start", 0),
            current_period_end=data.get("current_period_end", 0),
            cancel_at_period_end=data.get("cancel_at_period_end", False),
            metadata=dict(data.get("metadata", {})),
        )

    # -- Protocol methods --

    async def create_customer(self, data: CustomerCreate) -> CustomerData:
        """Create a Stripe customer."""
        params: dict[str, Any] = {"email": data.email}
        if data.name:
            params["name"] = data.name
        if data.metadata:
            params["metadata"] = data.metadata

        result = await self._request("POST", "/v1/customers", data=params)
        return self._parse_customer(result)

    async def get_customer(self, customer_id: str) -> CustomerData:
        """Retrieve a Stripe customer by ID."""
        result = await self._request("GET", f"/v1/customers/{customer_id}")
        return self._parse_customer(result)

    async def update_customer(
        self,
        customer_id: str,
        *,
        email: str = "",
        name: str = "",
        metadata: dict[str, str] | None = None,
    ) -> CustomerData:
        """Update a Stripe customer."""
        params: dict[str, Any] = {}
        if email:
            params["email"] = email
        if name:
            params["name"] = name
        if metadata is not None:
            params["metadata"] = metadata

        result = await self._request(
            "POST", f"/v1/customers/{customer_id}", data=params
        )
        return self._parse_customer(result)

    async def delete_customer(self, customer_id: str) -> bool:
        """Delete a Stripe customer."""
        result = await self._request(
            "DELETE", f"/v1/customers/{customer_id}"
        )
        return result.get("deleted", False)

    async def create_subscription(
        self, data: SubscriptionCreate
    ) -> SubscriptionData:
        """Create a Stripe subscription."""
        params: dict[str, Any] = {
            "customer": data.customer_id,
            "items": [{"price": data.price_id}],
        }
        if data.metadata:
            params["metadata"] = data.metadata
        if data.trial_period_days is not None:
            params["trial_period_days"] = data.trial_period_days

        result = await self._request(
            "POST", "/v1/subscriptions", data=params
        )
        return self._parse_subscription(result)

    async def get_subscription(
        self, subscription_id: str
    ) -> SubscriptionData:
        """Retrieve a Stripe subscription by ID."""
        result = await self._request(
            "GET", f"/v1/subscriptions/{subscription_id}"
        )
        return self._parse_subscription(result)

    async def cancel_subscription(
        self, subscription_id: str, *, at_period_end: bool = True
    ) -> SubscriptionData:
        """Cancel a Stripe subscription.

        If at_period_end is True, updates the subscription to cancel at
        period end. If False, deletes the subscription immediately.
        """
        if at_period_end:
            result = await self._request(
                "POST",
                f"/v1/subscriptions/{subscription_id}",
                data={"cancel_at_period_end": True},
            )
        else:
            result = await self._request(
                "DELETE", f"/v1/subscriptions/{subscription_id}"
            )

        return self._parse_subscription(result)

    async def create_checkout_session(
        self, data: CheckoutCreate
    ) -> CheckoutData:
        """Create a Stripe checkout session."""
        params: dict[str, Any] = {
            "customer": data.customer_id,
            "line_items": [{"price": data.price_id, "quantity": "1"}],
            "mode": str(data.mode),
            "success_url": data.success_url,
            "cancel_url": data.cancel_url,
        }
        if data.metadata:
            params["metadata"] = data.metadata

        result = await self._request(
            "POST", "/v1/checkout/sessions", data=params
        )
        return CheckoutData(
            id=result["id"],
            url=result.get("url", ""),
            status=result.get("status", ""),
        )

    async def create_portal_session(
        self, data: PortalCreate
    ) -> PortalData:
        """Create a Stripe billing portal session."""
        params: dict[str, Any] = {"customer": data.customer_id}
        if data.return_url:
            params["return_url"] = data.return_url

        result = await self._request(
            "POST", "/v1/billing_portal/sessions", data=params
        )
        return PortalData(
            id=result["id"],
            url=result.get("url", ""),
        )

    async def health_check(self) -> bool:
        """Check connectivity by fetching the account balance."""
        try:
            await self._request("GET", "/v1/balance")
            return True
        except Exception:
            return False

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()
