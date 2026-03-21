"""Email inbound webhook router."""

from __future__ import annotations

import asyncio
import hmac
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ulfblk_channels.models.message import ChannelType, InboundMessage


class EmailRouter:
    """Email inbound webhook handler.

    Accepts POST requests with JSON payload containing email data.
    Compatible with services like SendGrid Inbound Parse, Mailgun, etc.

    Example:
        email = EmailRouter(
            on_message=lambda msg: print(f"From: {msg.sender}"),
            webhook_secret="secret",
        )
        app.include_router(email.router, prefix="/email")
    """

    def __init__(
        self,
        on_message: Callable[[InboundMessage], Any] | None = None,
        webhook_secret: str | None = None,
    ) -> None:
        self.on_message = on_message
        self.webhook_secret = webhook_secret
        self._router = APIRouter()
        self._setup_routes()

    @property
    def router(self) -> APIRouter:
        """FastAPI router with webhook endpoint."""
        return self._router

    def _setup_routes(self) -> None:
        """Register POST route for inbound email webhook."""

        @self._router.post("")
        @self._router.post("/")
        async def receive(request: Request):
            """Receive and process inbound email webhook."""
            if self.webhook_secret is not None:
                token = request.headers.get("x-webhook-secret")
                if token is None or not hmac.compare_digest(
                    token, self.webhook_secret
                ):
                    return JSONResponse(
                        status_code=403,
                        content={"error": "invalid_webhook_secret"},
                    )

            body = await request.json()
            msg = self._parse_email(body)

            if msg is not None and self.on_message is not None:
                result = self.on_message(msg)
                if asyncio.iscoroutine(result):
                    await result

            return JSONResponse(status_code=200, content={"status": "ok"})

    def _parse_email(self, body: dict[str, Any]) -> InboundMessage | None:
        """Parse an inbound email webhook payload."""
        sender = body.get("from", body.get("sender", ""))
        text = body.get("text", body.get("body", ""))
        subject = body.get("subject", "")
        message_id = body.get("message_id", body.get("id", ""))

        if not sender and not text:
            return None

        timestamp_str = body.get("timestamp")
        if timestamp_str:
            try:
                ts = datetime.fromtimestamp(int(timestamp_str), tz=UTC)
            except (ValueError, OSError):
                ts = datetime.now(tz=UTC)
        else:
            ts = datetime.now(tz=UTC)

        return InboundMessage(
            channel=ChannelType.EMAIL,
            sender=sender,
            text=text,
            message_id=str(message_id),
            timestamp=ts,
            metadata={"subject": subject},
            raw=body,
        )
