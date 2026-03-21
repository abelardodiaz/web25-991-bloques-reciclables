"""Protocol for billing providers."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ulfblk_billing.models.checkout import CheckoutCreate, CheckoutData
from ulfblk_billing.models.customer import CustomerCreate, CustomerData
from ulfblk_billing.models.portal import PortalCreate, PortalData
from ulfblk_billing.models.subscription import (
    SubscriptionCreate,
    SubscriptionData,
)


@runtime_checkable
class BillingProvider(Protocol):
    """Protocol that all billing providers must satisfy.

    Duck-typed: any object implementing these methods can be used
    as a provider without inheriting this class.

    Example:
        class PaddleProvider:
            async def create_customer(self, data):
                ...
            async def health_check(self) -> bool:
                return True
            # ... all other methods
    """

    async def create_customer(self, data: CustomerCreate) -> CustomerData: ...

    async def get_customer(self, customer_id: str) -> CustomerData: ...

    async def update_customer(
        self,
        customer_id: str,
        *,
        email: str = "",
        name: str = "",
        metadata: dict[str, str] | None = None,
    ) -> CustomerData: ...

    async def delete_customer(self, customer_id: str) -> bool: ...

    async def create_subscription(
        self, data: SubscriptionCreate
    ) -> SubscriptionData: ...

    async def get_subscription(
        self, subscription_id: str
    ) -> SubscriptionData: ...

    async def cancel_subscription(
        self, subscription_id: str, *, at_period_end: bool = True
    ) -> SubscriptionData: ...

    async def create_checkout_session(
        self, data: CheckoutCreate
    ) -> CheckoutData: ...

    async def create_portal_session(
        self, data: PortalCreate
    ) -> PortalData: ...

    async def health_check(self) -> bool: ...
