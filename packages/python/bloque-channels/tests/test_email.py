"""Tests for Email inbound webhook router and outbound client."""


import pytest
from bloque_channels.email.router import EmailRouter
from bloque_channels.models.message import ChannelType
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


def _make_email_payload(sender="user@example.com", text="Hello", subject="Test"):
    return {
        "from": sender,
        "text": text,
        "subject": subject,
        "message_id": "msg-001",
        "timestamp": "1700000000",
    }


@pytest.mark.asyncio
async def test_receive_email_webhook():
    received = []

    app = FastAPI()
    email = EmailRouter(on_message=lambda msg: received.append(msg))
    app.include_router(email.router, prefix="/email")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/email", json=_make_email_payload("alice@test.com", "Hi there")
        )
        assert response.status_code == 200
        assert len(received) == 1
        assert received[0].sender == "alice@test.com"
        assert received[0].text == "Hi there"
        assert received[0].channel == ChannelType.EMAIL
        assert received[0].metadata["subject"] == "Test"


@pytest.mark.asyncio
async def test_receive_email_with_secret_valid():
    received = []

    app = FastAPI()
    email = EmailRouter(
        on_message=lambda msg: received.append(msg),
        webhook_secret="my-secret",
    )
    app.include_router(email.router, prefix="/email")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/email",
            json=_make_email_payload(),
            headers={"x-webhook-secret": "my-secret"},
        )
        assert response.status_code == 200
        assert len(received) == 1


@pytest.mark.asyncio
async def test_receive_email_with_secret_invalid():
    app = FastAPI()
    email = EmailRouter(
        on_message=lambda msg: None,
        webhook_secret="correct-secret",
    )
    app.include_router(email.router, prefix="/email")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/email",
            json=_make_email_payload(),
            headers={"x-webhook-secret": "wrong"},
        )
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_receive_email_empty_payload():
    received = []

    app = FastAPI()
    email = EmailRouter(on_message=lambda msg: received.append(msg))
    app.include_router(email.router, prefix="/email")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/email", json={})
        assert response.status_code == 200
        assert len(received) == 0


@pytest.mark.asyncio
async def test_email_client_import_error():
    """EmailClient.send_text raises ImportError if aiosmtplib is missing."""
    from unittest.mock import patch as _patch

    from bloque_channels.email.client import EmailClient
    from bloque_channels.models.settings import EmailSettings

    client = EmailClient(EmailSettings())

    with _patch.dict("sys.modules", {"aiosmtplib": None}):
        with pytest.raises(ImportError, match="aiosmtplib"):
            await client.send_text("to@test.com", "Subject", "Body")
