"""Tests for WhatsApp webhook router, client, and signature verification."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from ulfblk_channels.models.message import ChannelType
from ulfblk_channels.whatsapp.client import WhatsAppClient
from ulfblk_channels.whatsapp.router import WhatsAppRouter
from ulfblk_channels.whatsapp.signature import verify_whatsapp_signature
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


def _make_wa_payload(text="Hola", sender="5215512345678", msg_id="wamid.abc"):
    """Build a minimal WhatsApp webhook payload."""
    return {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": sender,
                                    "id": msg_id,
                                    "timestamp": "1700000000",
                                    "type": "text",
                                    "text": {"body": text},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }


# --- Signature tests ---


def test_verify_signature_valid():
    import hashlib
    import hmac as _hmac

    secret = "my-app-secret"
    payload = b'{"test": true}'
    sig = "sha256=" + _hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    assert verify_whatsapp_signature(payload, sig, secret) is True


def test_verify_signature_invalid():
    assert verify_whatsapp_signature(b"data", "sha256=bad", "secret") is False


def test_verify_signature_no_prefix():
    assert verify_whatsapp_signature(b"data", "invalid", "secret") is False


# --- Router verification (GET) tests ---


@pytest.mark.asyncio
async def test_verify_success():
    app = FastAPI()
    wa = WhatsAppRouter(verify_token="my-token")
    app.include_router(wa.router, prefix="/webhook")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "my-token",
                "hub.challenge": "challenge-123",
            },
        )
        assert response.status_code == 200
        assert response.text == "challenge-123"


@pytest.mark.asyncio
async def test_verify_wrong_token():
    app = FastAPI()
    wa = WhatsAppRouter(verify_token="correct-token")
    app.include_router(wa.router, prefix="/webhook")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "wrong-token",
                "hub.challenge": "challenge-123",
            },
        )
        assert response.status_code == 403


# --- Router message handling (POST) tests ---


@pytest.mark.asyncio
async def test_receive_text_message():
    received = []

    app = FastAPI()
    wa = WhatsAppRouter(
        verify_token="token",
        on_message=lambda msg: received.append(msg),
    )
    app.include_router(wa.router, prefix="/webhook")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/webhook", json=_make_wa_payload("Hola mundo")
        )
        assert response.status_code == 200
        assert len(received) == 1
        assert received[0].text == "Hola mundo"
        assert received[0].channel == ChannelType.WHATSAPP
        assert received[0].sender == "5215512345678"


@pytest.mark.asyncio
async def test_receive_async_callback():
    received = []

    async def handler(msg):
        received.append(msg)

    app = FastAPI()
    wa = WhatsAppRouter(verify_token="token", on_message=handler)
    app.include_router(wa.router, prefix="/webhook")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/webhook", json=_make_wa_payload("Async msg"))
        assert len(received) == 1
        assert received[0].text == "Async msg"


@pytest.mark.asyncio
async def test_receive_no_callback():
    app = FastAPI()
    wa = WhatsAppRouter(verify_token="token", on_message=None)
    app.include_router(wa.router, prefix="/webhook")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/webhook", json=_make_wa_payload())
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_receive_non_text_ignored():
    received = []

    app = FastAPI()
    wa = WhatsAppRouter(
        verify_token="token",
        on_message=lambda msg: received.append(msg),
    )
    app.include_router(wa.router, prefix="/webhook")

    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {"type": "image", "from": "123", "id": "x"}
                            ]
                        }
                    }
                ]
            }
        ]
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/webhook", json=payload)
        assert len(received) == 0


# --- Client tests ---


@pytest.mark.asyncio
async def test_client_not_started():
    from ulfblk_channels.models.settings import WhatsAppSettings as WaS
    client = WhatsAppClient(WaS())
    with pytest.raises(RuntimeError, match="not started"):
        _ = client.client


@pytest.mark.asyncio
async def test_client_send_text(wa_settings):
    client = WhatsAppClient(wa_settings)
    await client.start()

    mock_request = httpx.Request(
        "POST", "https://graph.facebook.com/v21.0/123456789/messages"
    )
    mock_response = httpx.Response(
        200, json={"messages": [{"id": "wamid.ok"}]},
        request=mock_request,
    )

    with patch.object(client.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        result = await client.send_text("+5215512345678", "Test")
        assert result["messages"][0]["id"] == "wamid.ok"
        mock_post.assert_called_once()

    await client.stop()


@pytest.mark.asyncio
async def test_client_circuit_breaker_on_failure(wa_settings):
    from unittest.mock import MagicMock
    cb = MagicMock()
    client = WhatsAppClient(wa_settings, circuit_breaker=cb)
    await client.start()

    with patch.object(
        client.client,
        "post",
        new_callable=AsyncMock,
        side_effect=httpx.ConnectError("refused"),
    ):
        with pytest.raises(httpx.ConnectError):
            await client.send_text("+5215512345678", "Fail")
        cb.record_failure.assert_called_once()

    await client.stop()
