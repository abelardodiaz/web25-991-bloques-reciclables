"""WhatsApp client for sending messages via Meta Cloud API."""

from __future__ import annotations

from typing import Any

import httpx

from ulfblk_channels.models.message import OutboundMessage
from ulfblk_channels.models.settings import WhatsAppSettings


class WhatsAppClient:
    """Send text messages through WhatsApp Meta Cloud API.

    Supports optional circuit_breaker (duck-typed) for resilience.

    Example:
        client = WhatsAppClient(settings)
        await client.start()
        await client.send_text("+5215512345678", "Hola!")
        await client.stop()
    """

    def __init__(
        self,
        settings: WhatsAppSettings,
        http_client: httpx.AsyncClient | None = None,
        circuit_breaker: object | None = None,
    ) -> None:
        self.settings = settings
        self._external_client = http_client is not None
        self._client = http_client
        self._circuit_breaker = circuit_breaker

    async def start(self) -> None:
        """Create the httpx.AsyncClient if not provided externally."""
        if self._client is not None:
            return
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
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
                "WhatsAppClient is not started. Call start() or use async with."
            )
        return self._client

    async def send_text(self, to: str, text: str) -> dict[str, Any]:
        """Send a text message to a WhatsApp number.

        Args:
            to: Recipient phone number (international format).
            text: Message text to send.

        Returns:
            API response as dict.
        """
        url = (
            f"{self.settings.api_base_url}/{self.settings.api_version}"
            f"/{self.settings.phone_number_id}/messages"
        )
        headers = {
            "Authorization": f"Bearer {self.settings.api_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text},
        }

        try:
            response = await self.client.post(
                url, json=payload, headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            if self._circuit_breaker is not None:
                self._circuit_breaker.record_failure()  # type: ignore[attr-defined]
            raise exc

    async def send_message(self, message: OutboundMessage) -> dict[str, Any]:
        """Send a message using the ChannelProtocol interface."""
        return await self.send_text(message.recipient, message.text)

    async def health_check(self) -> bool:
        """Check if the WhatsApp API is reachable."""
        try:
            url = (
                f"{self.settings.api_base_url}/{self.settings.api_version}"
                f"/{self.settings.phone_number_id}"
            )
            headers = {
                "Authorization": f"Bearer {self.settings.api_token}",
            }
            response = await self.client.get(url, headers=headers, timeout=5.0)
            return response.status_code < 500
        except Exception:
            return False

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()
