"""Telegram webhook router: receives Bot API updates."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ulfblk_channels.models.message import ChannelType, InboundMessage
from ulfblk_channels.models.settings import TelegramSettings
from ulfblk_channels.telegram.client import TelegramClient
from ulfblk_channels.telegram.signature import verify_telegram_secret


class TelegramRouter:
    """Telegram webhook handler for Bot API updates.

    Example:
        telegram = TelegramRouter(
            on_message=lambda msg: print(msg.text),
            secret_token="mi-secret",
        )
        app.include_router(telegram.router, prefix="/telegram")
    """

    def __init__(
        self,
        on_message: Callable[[InboundMessage], Any] | None = None,
        settings: TelegramSettings | None = None,
        client: TelegramClient | None = None,
        secret_token: str | None = None,
    ) -> None:
        self.on_message = on_message
        self.settings = settings
        self.client = client
        self.secret_token = secret_token
        self._router = APIRouter()
        self._setup_routes()

    @property
    def router(self) -> APIRouter:
        """FastAPI router with webhook endpoint."""
        return self._router

    def _setup_routes(self) -> None:
        """Register POST route for Telegram updates."""

        @self._router.post("")
        @self._router.post("/")
        async def receive(request: Request):
            """Receive and process Telegram webhook updates."""
            if self.secret_token is not None:
                request_token = request.headers.get(
                    "x-telegram-bot-api-secret-token"
                )
                if not verify_telegram_secret(request_token, self.secret_token):
                    return JSONResponse(
                        status_code=403,
                        content={"error": "invalid_secret_token"},
                    )

            body = await request.json()
            msg = self._parse_update(body)

            if msg is not None and self.on_message is not None:
                result = self.on_message(msg)
                if asyncio.iscoroutine(result):
                    await result

            return JSONResponse(status_code=200, content={"status": "ok"})

    def _parse_update(self, body: dict[str, Any]) -> InboundMessage | None:
        """Extract a text message from a Telegram Update object."""
        message = body.get("message")
        if message is None:
            return None

        text = message.get("text")
        if text is None:
            return None

        chat = message.get("chat", {})
        sender = message.get("from", {})

        timestamp_unix = message.get("date", 0)
        try:
            ts = datetime.fromtimestamp(timestamp_unix, tz=UTC)
        except (ValueError, OSError):
            ts = datetime.now(tz=UTC)

        return InboundMessage(
            channel=ChannelType.TELEGRAM,
            sender=str(chat.get("id", sender.get("id", ""))),
            text=text,
            message_id=str(message.get("message_id", "")),
            timestamp=ts,
            raw=body,
        )
