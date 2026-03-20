"""Tests for BillingProvider protocol."""

from bloque_billing.models.settings import BillingSettings
from bloque_billing.protocol.provider import BillingProvider
from bloque_billing.providers.stripe import StripeProvider


class TestBillingProvider:
    def test_stripe_satisfies_protocol(self):
        """StripeProvider must satisfy BillingProvider protocol."""
        provider = StripeProvider(BillingSettings(api_key="sk_test_x"))
        assert isinstance(provider, BillingProvider)

    def test_duck_typed_class_satisfies(self):
        """A class with matching methods satisfies the protocol."""

        class FakeProvider:
            async def create_customer(self, data): ...
            async def get_customer(self, customer_id): ...
            async def update_customer(self, customer_id, *, email="", name="", metadata=None): ...
            async def delete_customer(self, customer_id): ...
            async def create_subscription(self, data): ...
            async def get_subscription(self, subscription_id): ...
            async def cancel_subscription(self, subscription_id, *, at_period_end=True): ...
            async def create_checkout_session(self, data): ...
            async def create_portal_session(self, data): ...
            async def health_check(self): ...

        assert isinstance(FakeProvider(), BillingProvider)

    def test_incomplete_class_fails(self):
        """A class missing methods does not satisfy the protocol."""

        class Incomplete:
            async def create_customer(self, data): ...

        assert not isinstance(Incomplete(), BillingProvider)
