"""Billing service orchestrator with tenant awareness."""

from __future__ import annotations

import logging
from typing import Any

from ulfblk_billing.models.checkout import CheckoutCreate, CheckoutData
from ulfblk_billing.models.customer import CustomerCreate, CustomerData
from ulfblk_billing.models.portal import PortalCreate, PortalData
from ulfblk_billing.models.settings import BillingSettings
from ulfblk_billing.models.subscription import (
    SubscriptionCreate,
    SubscriptionData,
)
from ulfblk_billing.models.webhook import WebhookEvent
from ulfblk_billing.webhooks.processor import WebhookProcessor

logger = logging.getLogger(__name__)


class BillingService:
    """Orchestrate billing operations with optional tenant awareness.

    Delegates to a BillingProvider (duck-typed) and injects tenant_id
    into metadata when tenant_aware is enabled.

    Args:
        provider: Any object satisfying the BillingProvider protocol.
        settings: Billing configuration.
        webhook_processor: Optional pre-configured webhook processor.

    Example:
        service = BillingService(provider, settings=settings)
        async with service:
            customer = await service.create_customer(
                CustomerCreate(email="user@example.com")
            )
    """

    def __init__(
        self,
        provider: Any,
        *,
        settings: BillingSettings | None = None,
        webhook_processor: WebhookProcessor | None = None,
    ) -> None:
        self.settings = settings or BillingSettings()
        self._provider = provider
        self._webhook_processor = webhook_processor

    async def start(self) -> None:
        """Start the provider if it has a start() method."""
        if hasattr(self._provider, "start"):
            await self._provider.start()
            logger.debug("Started billing provider")

    async def stop(self) -> None:
        """Stop the provider if it has a stop() method."""
        if hasattr(self._provider, "stop"):
            await self._provider.stop()
            logger.debug("Stopped billing provider")

    # -- Customer operations --

    async def create_customer(self, data: CustomerCreate) -> CustomerData:
        """Create a customer, injecting tenant_id if tenant_aware."""
        self._inject_tenant(data)
        return await self._provider.create_customer(data)

    async def get_customer(self, customer_id: str) -> CustomerData:
        """Retrieve a customer by ID."""
        return await self._provider.get_customer(customer_id)

    async def update_customer(
        self,
        customer_id: str,
        *,
        email: str = "",
        name: str = "",
        metadata: dict[str, str] | None = None,
    ) -> CustomerData:
        """Update a customer."""
        return await self._provider.update_customer(
            customer_id, email=email, name=name, metadata=metadata
        )

    async def delete_customer(self, customer_id: str) -> bool:
        """Delete a customer."""
        return await self._provider.delete_customer(customer_id)

    # -- Subscription operations --

    async def create_subscription(
        self, data: SubscriptionCreate
    ) -> SubscriptionData:
        """Create a subscription."""
        return await self._provider.create_subscription(data)

    async def get_subscription(
        self, subscription_id: str
    ) -> SubscriptionData:
        """Retrieve a subscription by ID."""
        return await self._provider.get_subscription(subscription_id)

    async def cancel_subscription(
        self, subscription_id: str, *, at_period_end: bool = True
    ) -> SubscriptionData:
        """Cancel a subscription."""
        return await self._provider.cancel_subscription(
            subscription_id, at_period_end=at_period_end
        )

    # -- Checkout & Portal --

    async def create_checkout_session(
        self, data: CheckoutCreate
    ) -> CheckoutData:
        """Create a checkout session."""
        return await self._provider.create_checkout_session(data)

    async def create_portal_session(
        self, data: PortalCreate
    ) -> PortalData:
        """Create a billing portal session."""
        return await self._provider.create_portal_session(data)

    # -- Webhooks --

    async def process_webhook(
        self, payload: bytes, signature_header: str
    ) -> WebhookEvent:
        """Process a webhook event using the configured processor.

        Raises:
            RuntimeError: If no webhook_processor was configured.
            ValueError: If signature verification fails.
        """
        if self._webhook_processor is None:
            raise RuntimeError("No webhook processor configured")
        return await self._webhook_processor.process(
            payload, signature_header
        )

    # -- Tenant helpers --

    def _inject_tenant(self, data: CustomerCreate) -> None:
        """Inject tenant_id into customer metadata if tenant_aware.

        Priority: explicit tenant_id on data > context tenant > nothing.
        """
        tenant_id = data.tenant_id
        if tenant_id is None and self.settings.tenant_aware:
            tenant_id = self._resolve_tenant()

        if tenant_id:
            data.metadata["tenant_id"] = tenant_id

    @staticmethod
    def _resolve_tenant() -> str | None:
        """Try to read tenant from ulfblk_multitenant context."""
        try:
            from ulfblk_multitenant.context import get_current_tenant

            ctx = get_current_tenant()
            return ctx.tenant_id if ctx else None
        except ImportError:
            return None

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()
