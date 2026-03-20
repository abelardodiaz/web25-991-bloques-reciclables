"""Tests for WebhookProcessor."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from bloque_billing.webhooks.processor import WebhookProcessor


@pytest.fixture
def processor(settings):
    return WebhookProcessor(settings.webhook_secret)


class TestWebhookProcessor:
    @pytest.mark.asyncio
    async def test_process_valid_event(self, processor, settings, make_signature, make_payload):
        payload = make_payload(event_type="customer.created")
        sig = make_signature(payload, settings.webhook_secret)

        event = await processor.process(payload, sig)
        assert event.event_type == "customer.created"
        assert event.id == "evt_test_123"

    @pytest.mark.asyncio
    async def test_process_dispatches_handler(
        self, processor, settings, make_signature, make_payload,
    ):
        handler = AsyncMock()
        processor.on("customer.created", handler)

        payload = make_payload(event_type="customer.created")
        sig = make_signature(payload, settings.webhook_secret)

        await processor.process(payload, sig)
        handler.assert_awaited_once()
        assert handler.call_args[0][0].event_type == "customer.created"

    @pytest.mark.asyncio
    async def test_process_invalid_signature(self, processor, make_payload):
        payload = make_payload()
        with pytest.raises(ValueError):
            await processor.process(payload, "t=0,v1=invalid")

    @pytest.mark.asyncio
    async def test_handler_error_does_not_propagate(
        self, processor, settings, make_signature, make_payload,
    ):
        handler = AsyncMock(side_effect=RuntimeError("boom"))
        processor.on("customer.created", handler)

        payload = make_payload(event_type="customer.created")
        sig = make_signature(payload, settings.webhook_secret)

        event = await processor.process(payload, sig)
        assert event.event_type == "customer.created"

    @pytest.mark.asyncio
    async def test_unhandled_event_type(self, processor, settings, make_signature, make_payload):
        payload = make_payload(event_type="invoice.paid")
        sig = make_signature(payload, settings.webhook_secret)

        event = await processor.process(payload, sig)
        assert event.event_type == "invoice.paid"
