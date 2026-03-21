"""Telegram client for sending messages via Bot API."""

from __future__ import annotations

from typing import Any

import httpx

from ulfblk_channels.models.message import OutboundMessage
from ulfblk_channels.models.settings import TelegramSettings


class TelegramClient:
    """Send text messages through Telegram Bot API.

    Supports optional circuit_breaker (duck-typed) for resilience.

    Example:
        client = TelegramClient(settings)
        await client.start()
        await client.send_text("123456789", "Hola!")
        await client.stop()
    """

    def __init__(
        self,
        settings: TelegramSettings,
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
                "TelegramClient is not started. Call start() or use async with."
            )
        return self._client

    async def send_text(self, chat_id: str | int, text: str) -> dict[str, Any]:
        """Send a text message to a Telegram chat.

        Args:
            chat_id: Telegram chat ID (user, group, or channel).
            text: Message text to send.

        Returns:
            API response as dict.
        """
        url = (
            f"{self.settings.api_base_url}/bot{self.settings.bot_token}"
            "/sendMessage"
        )
        payload = {
            "chat_id": chat_id,
            "text": text,
        }

        try:
            response = await self.client.post(url, json=payload)
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
        """Check if the Telegram Bot API is reachable."""
        try:
            url = (
                f"{self.settings.api_base_url}/bot{self.settings.bot_token}"
                "/getMe"
            )
            response = await self.client.get(url, timeout=5.0)
            return response.status_code < 500
        except Exception:
            return False

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()
