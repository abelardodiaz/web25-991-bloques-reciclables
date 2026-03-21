"""Webhook notification provider."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from ulfblk_notifications.models.settings import WebhookProviderSettings

logger = logging.getLogger(__name__)


class WebhookProvider:
    """Send notifications via HTTP POST to a webhook URL.

    POSTs a JSON payload with subject, body, and metadata to the
    recipient URL (or default_url from settings).

    Args:
        settings: Webhook provider configuration.
        http_client: Optional pre-configured httpx.AsyncClient.

    Example:
        provider = WebhookProvider(WebhookProviderSettings(
            default_url="https://hooks.example.com/notify",
        ))
        async with provider:
            await provider.send("https://alt.example.com/hook", "Alert", "Server down")
    """

    def __init__(
        self,
        settings: WebhookProviderSettings | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings or WebhookProviderSettings()
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
                "WebhookProvider is not started. Call start() or use async with."
            )
        return self._client

    async def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """POST notification as JSON to the recipient URL.

        Args:
            recipient: Target URL. Falls back to settings.default_url if empty.
            subject: Notification subject.
            body: Notification body.
            metadata: Extra data included in the JSON payload.

        Returns:
            Dict with status_code and response body.

        Raises:
            RuntimeError: If provider is not started.
            ValueError: If no URL is available.
        """
        url = recipient or self.settings.default_url
        if not url:
            raise ValueError(
                "No recipient URL provided and no default_url configured."
            )

        payload: dict[str, Any] = {
            "subject": subject,
            "body": body,
        }
        if metadata:
            payload["metadata"] = metadata

        headers = dict(self.settings.headers)
        headers.setdefault("Content-Type", "application/json")

        response = await self.client.post(url, json=payload, headers=headers)
        response.raise_for_status()

        logger.debug("Webhook sent to %s: %d", url, response.status_code)
        return {
            "status_code": response.status_code,
            "response": response.text,
        }

    async def health_check(self) -> bool:
        """Check if the provider is operational."""
        return self._client is not None

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()
