"""Webhook event processor with signature verification and dispatch."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from typing import Any

from bloque_billing.models.webhook import WebhookEvent
from bloque_billing.webhooks.signature import verify_stripe_signature

logger = logging.getLogger(__name__)


class WebhookProcessor:
    """Verify Stripe webhook signatures and dispatch to registered handlers.

    Example:
        processor = WebhookProcessor("whsec_...")

        async def on_checkout(event):
            print(event.data)

        processor.on("checkout.session.completed", on_checkout)
        event = await processor.process(payload, signature_header)
    """

    def __init__(self, webhook_secret: str, *, tolerance: int = 300) -> None:
        self._webhook_secret = webhook_secret
        self._tolerance = tolerance
        self._handlers: dict[str, list[Callable[..., Any]]] = {}

    def on(self, event_type: str, handler: Callable[..., Any]) -> None:
        """Register a handler for a specific event type.

        Args:
            event_type: Stripe event type string (e.g. "customer.created").
            handler: Async callable that receives a WebhookEvent.
        """
        self._handlers.setdefault(event_type, []).append(handler)

    async def process(
        self, payload: bytes, signature_header: str
    ) -> WebhookEvent:
        """Verify signature, parse event, and dispatch to handlers.

        Args:
            payload: Raw request body bytes.
            signature_header: Value of Stripe-Signature header.

        Returns:
            Parsed WebhookEvent.

        Raises:
            ValueError: If signature verification fails.
            json.JSONDecodeError: If payload is not valid JSON.
        """
        # Verify signature (raises ValueError on failure)
        verify_stripe_signature(
            payload,
            signature_header,
            self._webhook_secret,
            tolerance=self._tolerance,
        )

        # Parse event
        raw = json.loads(payload)
        event = WebhookEvent(
            id=raw.get("id", ""),
            event_type=raw.get("type", ""),
            data=raw.get("data", {}).get("object", {}),
            created=raw.get("created", 0),
        )

        # Dispatch to registered handlers
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception:
                logger.error(
                    "Handler failed for event %s (%s)",
                    event.id,
                    event.event_type,
                    exc_info=True,
                )

        return event
