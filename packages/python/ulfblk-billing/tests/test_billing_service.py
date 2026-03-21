"""Tests for BillingService orchestrator."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from ulfblk_billing.models.customer import CustomerCreate, CustomerData
from ulfblk_billing.models.settings import BillingSettings
from ulfblk_billing.models.subscription import SubscriptionData, SubscriptionStatus
from ulfblk_billing.service.billing_service import BillingService
from ulfblk_billing.webhooks.processor import WebhookProcessor


@pytest.fixture
def mock_provider():
    provider = AsyncMock()
    provider.create_customer = AsyncMock(
        return_value=CustomerData(id="cus_123", email="user@example.com")
    )
    provider.get_customer = AsyncMock(
        return_value=CustomerData(id="cus_123", email="user@example.com")
    )
    provider.delete_customer = AsyncMock(return_value=True)
    provider.cancel_subscription = AsyncMock(
        return_value=SubscriptionData(
            id="sub_123", customer_id="cus_123", status=SubscriptionStatus.CANCELED
        )
    )
    provider.start = AsyncMock()
    provider.stop = AsyncMock()
    return provider


class TestBillingServiceLifecycle:
    @pytest.mark.asyncio
    async def test_start_stop(self, mock_provider):
        service = BillingService(mock_provider)
        await service.start()
        mock_provider.start.assert_awaited_once()
        await service.stop()
        mock_provider.stop.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_provider):
        async with BillingService(mock_provider) as svc:
            assert svc is not None
        mock_provider.start.assert_awaited_once()
        mock_provider.stop.assert_awaited_once()


class TestBillingServiceCustomer:
    @pytest.mark.asyncio
    async def test_create_customer(self, mock_provider):
        service = BillingService(mock_provider)
        result = await service.create_customer(
            CustomerCreate(email="user@example.com")
        )
        assert result.id == "cus_123"
        mock_provider.create_customer.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_customer(self, mock_provider):
        service = BillingService(mock_provider)
        result = await service.get_customer("cus_123")
        assert result.email == "user@example.com"

    @pytest.mark.asyncio
    async def test_delete_customer(self, mock_provider):
        service = BillingService(mock_provider)
        result = await service.delete_customer("cus_123")
        assert result is True


class TestBillingServiceTenant:
    @pytest.mark.asyncio
    async def test_tenant_injection_explicit(self, mock_provider):
        settings = BillingSettings(tenant_aware=True)
        service = BillingService(mock_provider, settings=settings)

        data = CustomerCreate(email="u@example.com", tenant_id="t-1")
        await service.create_customer(data)
        assert data.metadata["tenant_id"] == "t-1"

    @pytest.mark.asyncio
    async def test_tenant_injection_from_context(self, mock_provider):
        settings = BillingSettings(tenant_aware=True)
        service = BillingService(mock_provider, settings=settings)

        with patch.object(
            BillingService,
            "_resolve_tenant",
            return_value="ctx-tenant",
        ):
            data = CustomerCreate(email="u@example.com")
            await service.create_customer(data)
            assert data.metadata["tenant_id"] == "ctx-tenant"

    @pytest.mark.asyncio
    async def test_no_tenant_when_disabled(self, mock_provider):
        settings = BillingSettings(tenant_aware=False)
        service = BillingService(mock_provider, settings=settings)

        data = CustomerCreate(email="u@example.com")
        await service.create_customer(data)
        assert "tenant_id" not in data.metadata


class TestBillingServiceWebhook:
    @pytest.mark.asyncio
    async def test_process_webhook(self, mock_provider, make_signature, make_payload):
        secret = "whsec_test"
        processor = WebhookProcessor(secret)
        service = BillingService(
            mock_provider,
            webhook_processor=processor,
        )

        payload = make_payload(event_type="customer.created")
        sig = make_signature(payload, secret)

        event = await service.process_webhook(payload, sig)
        assert event.event_type == "customer.created"

    @pytest.mark.asyncio
    async def test_process_webhook_no_processor(self, mock_provider):
        service = BillingService(mock_provider)
        with pytest.raises(RuntimeError, match="No webhook processor"):
            await service.process_webhook(b"body", "sig")
