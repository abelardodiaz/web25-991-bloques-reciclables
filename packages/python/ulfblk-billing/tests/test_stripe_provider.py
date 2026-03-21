"""Tests for StripeProvider (httpx, form-encoded)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from ulfblk_billing.models.checkout import CheckoutCreate, CheckoutMode
from ulfblk_billing.models.customer import CustomerCreate
from ulfblk_billing.models.portal import PortalCreate
from ulfblk_billing.models.subscription import SubscriptionCreate, SubscriptionStatus
from ulfblk_billing.providers.stripe import StripeProvider


def _mock_response(data: dict) -> MagicMock:
    """Create a mock httpx.Response."""
    resp = MagicMock()
    resp.json.return_value = data
    resp.raise_for_status = MagicMock()
    return resp


@pytest.fixture
def provider(settings, mock_http_client):
    """StripeProvider with mocked http client."""
    p = StripeProvider(settings, http_client=mock_http_client)
    return p


class TestFlattenParams:
    def test_simple(self):
        result = StripeProvider._flatten_params({"email": "a@b.com", "name": "Jo"})
        assert result == {"email": "a@b.com", "name": "Jo"}

    def test_nested_metadata(self):
        result = StripeProvider._flatten_params(
            {"metadata": {"tenant_id": "abc", "plan": "pro"}}
        )
        assert result == {
            "metadata[tenant_id]": "abc",
            "metadata[plan]": "pro",
        }

    def test_list_items(self):
        result = StripeProvider._flatten_params(
            {"items": [{"price": "price_xxx"}]}
        )
        assert result == {"items[0][price]": "price_xxx"}

    def test_boolean(self):
        result = StripeProvider._flatten_params({"cancel_at_period_end": True})
        assert result == {"cancel_at_period_end": "true"}

    def test_none_skipped(self):
        result = StripeProvider._flatten_params({"a": "x", "b": None})
        assert result == {"a": "x"}


class TestStripeProviderLifecycle:
    @pytest.mark.asyncio
    async def test_start_creates_client(self, settings):
        p = StripeProvider(settings)
        assert p._client is None
        await p.start()
        assert p._client is not None
        await p.stop()

    @pytest.mark.asyncio
    async def test_external_client_not_closed(self, settings, mock_http_client):
        p = StripeProvider(settings, http_client=mock_http_client)
        await p.start()
        await p.stop()
        mock_http_client.aclose.assert_not_awaited()

    def test_client_property_raises_before_start(self, settings):
        p = StripeProvider(settings)
        with pytest.raises(RuntimeError, match="not started"):
            _ = p.client


class TestStripeProviderCustomer:
    @pytest.mark.asyncio
    async def test_create_customer(self, provider, mock_http_client):
        mock_http_client.request.return_value = _mock_response({
            "id": "cus_abc",
            "email": "user@example.com",
            "name": "Jane",
            "metadata": {},
            "created": 1700000000,
        })

        result = await provider.create_customer(
            CustomerCreate(email="user@example.com", name="Jane")
        )
        assert result.id == "cus_abc"
        assert result.email == "user@example.com"

        call = mock_http_client.request.call_args
        assert call[0][0] == "POST"
        assert "/v1/customers" in call[0][1]

    @pytest.mark.asyncio
    async def test_delete_customer(self, provider, mock_http_client):
        mock_http_client.request.return_value = _mock_response({
            "id": "cus_abc",
            "deleted": True,
        })
        result = await provider.delete_customer("cus_abc")
        assert result is True


class TestStripeProviderSubscription:
    @pytest.mark.asyncio
    async def test_create_subscription(self, provider, mock_http_client):
        mock_http_client.request.return_value = _mock_response({
            "id": "sub_123",
            "customer": "cus_abc",
            "status": "active",
            "items": {"data": [{"price": {"id": "price_xxx"}}]},
            "current_period_start": 1700000000,
            "current_period_end": 1702592000,
            "cancel_at_period_end": False,
            "metadata": {},
        })

        result = await provider.create_subscription(
            SubscriptionCreate(customer_id="cus_abc", price_id="price_xxx")
        )
        assert result.id == "sub_123"
        assert result.status == SubscriptionStatus.ACTIVE
        assert result.price_id == "price_xxx"

    @pytest.mark.asyncio
    async def test_cancel_at_period_end(self, provider, mock_http_client):
        mock_http_client.request.return_value = _mock_response({
            "id": "sub_123",
            "customer": "cus_abc",
            "status": "active",
            "cancel_at_period_end": True,
            "metadata": {},
        })

        result = await provider.cancel_subscription("sub_123", at_period_end=True)
        assert result.cancel_at_period_end is True

        call = mock_http_client.request.call_args
        assert call[0][0] == "POST"

    @pytest.mark.asyncio
    async def test_cancel_immediate(self, provider, mock_http_client):
        mock_http_client.request.return_value = _mock_response({
            "id": "sub_123",
            "customer": "cus_abc",
            "status": "canceled",
            "cancel_at_period_end": False,
            "metadata": {},
        })

        result = await provider.cancel_subscription("sub_123", at_period_end=False)
        assert result.status == SubscriptionStatus.CANCELED

        call = mock_http_client.request.call_args
        assert call[0][0] == "DELETE"


class TestStripeProviderCheckout:
    @pytest.mark.asyncio
    async def test_create_checkout_session(self, provider, mock_http_client):
        mock_http_client.request.return_value = _mock_response({
            "id": "cs_test_123",
            "url": "https://checkout.stripe.com/pay/cs_test_123",
            "status": "open",
        })

        result = await provider.create_checkout_session(
            CheckoutCreate(
                customer_id="cus_abc",
                price_id="price_xxx",
                success_url="https://example.com/ok",
                cancel_url="https://example.com/cancel",
                mode=CheckoutMode.SUBSCRIPTION,
            )
        )
        assert result.id == "cs_test_123"
        assert "checkout.stripe.com" in result.url


class TestStripeProviderPortal:
    @pytest.mark.asyncio
    async def test_create_portal_session(self, provider, mock_http_client):
        mock_http_client.request.return_value = _mock_response({
            "id": "bps_test_123",
            "url": "https://billing.stripe.com/session/bps_test_123",
        })

        result = await provider.create_portal_session(
            PortalCreate(customer_id="cus_abc", return_url="https://app.example.com")
        )
        assert result.id == "bps_test_123"
        assert "billing.stripe.com" in result.url


class TestStripeProviderHealth:
    @pytest.mark.asyncio
    async def test_health_ok(self, provider, mock_http_client):
        mock_http_client.request.return_value = _mock_response({"available": []})
        assert await provider.health_check() is True

    @pytest.mark.asyncio
    async def test_health_fail(self, provider, mock_http_client):
        mock_http_client.request.side_effect = Exception("Connection refused")
        assert await provider.health_check() is False
