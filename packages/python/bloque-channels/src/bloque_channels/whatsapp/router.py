"""WhatsApp webhook router: verification (GET) and message handling (POST)."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from bloque_channels.models.message import ChannelType, InboundMessage
from bloque_channels.models.settings import WhatsAppSettings
from bloque_channels.whatsapp.client import WhatsAppClient


class WhatsAppRouter:
    """WhatsApp webhook handler with verify and message endpoints.

    Example:
        whatsapp = WhatsAppRouter(
            verify_token="mi-token",
            on_message=lambda msg: print(msg.text),
        )
        app.include_router(whatsapp.router, prefix="/webhook")
    """

    def __init__(
        self,
        verify_token: str,
        on_message: Callable[[InboundMessage], Any] | None = None,
        settings: WhatsAppSettings | None = None,
        client: WhatsAppClient | None = None,
    ) -> None:
        self.verify_token = verify_token
        self.on_message = on_message
        self.settings = settings
        self.client = client
        self._router = APIRouter()
        self._setup_routes()

    @property
    def router(self) -> APIRouter:
        """FastAPI router with webhook endpoints."""
        return self._router

    def _setup_routes(self) -> None:
        """Register GET (verify) and POST (message) routes."""

        @self._router.get("")
        @self._router.get("/")
        async def verify(
            hub_mode: str | None = Query(None, alias="hub.mode"),
            hub_verify_token: str | None = Query(None, alias="hub.verify_token"),
            hub_challenge: str | None = Query(None, alias="hub.challenge"),
        ):
            """Meta webhook verification endpoint."""
            if hub_mode == "subscribe" and hub_verify_token == self.verify_token:
                return PlainTextResponse(content=hub_challenge or "")
            return JSONResponse(
                status_code=403,
                content={"error": "verification_failed"},
            )

        @self._router.post("")
        @self._router.post("/")
        async def receive(request: Request):
            """Receive and process WhatsApp webhook messages."""
            body = await request.json()
            messages = self._parse_messages(body)

            for msg in messages:
                if self.on_message is not None:
                    result = self.on_message(msg)
                    if asyncio.iscoroutine(result):
                        await result

            return JSONResponse(status_code=200, content={"status": "ok"})

    def _parse_messages(self, body: dict[str, Any]) -> list[InboundMessage]:
        """Extract text messages from a WhatsApp webhook payload."""
        messages: list[InboundMessage] = []

        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for msg in value.get("messages", []):
                    if msg.get("type") != "text":
                        continue

                    timestamp_str = msg.get("timestamp", "0")
                    try:
                        ts = datetime.fromtimestamp(
                            int(timestamp_str), tz=UTC
                        )
                    except (ValueError, OSError):
                        ts = datetime.now(tz=UTC)

                    inbound = InboundMessage(
                        channel=ChannelType.WHATSAPP,
                        sender=msg.get("from", ""),
                        text=msg.get("text", {}).get("body", ""),
                        message_id=msg.get("id", ""),
                        timestamp=ts,
                        raw=msg,
                    )
                    messages.append(inbound)

        return messages
