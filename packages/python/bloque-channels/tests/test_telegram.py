"""Tests for Telegram webhook router, client, and secret verification."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from bloque_channels.models.message import ChannelType
from bloque_channels.telegram.client import TelegramClient
from bloque_channels.telegram.router import TelegramRouter
from bloque_channels.telegram.signature import verify_telegram_secret
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


def _make_tg_update(text="Hola", chat_id=12345, message_id=1):
    """Build a minimal Telegram Update payload."""
    return {
        "update_id": 100,
        "message": {
            "message_id": message_id,
            "from": {"id": chat_id, "first_name": "Test"},
            "chat": {"id": chat_id, "type": "private"},
            "date": 1700000000,
            "text": text,
        },
    }


# --- Signature tests ---


def test_verify_secret_valid():
    assert verify_telegram_secret("my-secret", "my-secret") is True


def test_verify_secret_invalid():
    assert verify_telegram_secret("wrong", "expected") is False


def test_verify_secret_none():
    assert verify_telegram_secret(None, "expected") is False


# --- Router tests ---


@pytest.mark.asyncio
async def test_receive_text_message():
    received = []

    app = FastAPI()
    tg = TelegramRouter(on_message=lambda msg: received.append(msg))
    app.include_router(tg.router, prefix="/telegram")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/telegram", json=_make_tg_update("Hola Telegram")
        )
        assert response.status_code == 200
        assert len(received) == 1
        assert received[0].text == "Hola Telegram"
        assert received[0].channel == ChannelType.TELEGRAM
        assert received[0].sender == "12345"


@pytest.mark.asyncio
async def test_receive_with_secret_valid():
    received = []

    app = FastAPI()
    tg = TelegramRouter(
        on_message=lambda msg: received.append(msg),
        secret_token="my-secret",
    )
    app.include_router(tg.router, prefix="/telegram")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/telegram",
            json=_make_tg_update("Secret msg"),
            headers={"x-telegram-bot-api-secret-token": "my-secret"},
        )
        assert response.status_code == 200
        assert len(received) == 1


@pytest.mark.asyncio
async def test_receive_with_secret_invalid():
    app = FastAPI()
    tg = TelegramRouter(
        on_message=lambda msg: None,
        secret_token="correct-secret",
    )
    app.include_router(tg.router, prefix="/telegram")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/telegram",
            json=_make_tg_update(),
            headers={"x-telegram-bot-api-secret-token": "wrong"},
        )
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_receive_non_text_ignored():
    received = []

    app = FastAPI()
    tg = TelegramRouter(on_message=lambda msg: received.append(msg))
    app.include_router(tg.router, prefix="/telegram")

    payload = {"update_id": 200, "message": {"message_id": 2, "chat": {"id": 1}, "photo": []}}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/telegram", json=payload)
        assert len(received) == 0


@pytest.mark.asyncio
async def test_receive_no_message_field():
    received = []

    app = FastAPI()
    tg = TelegramRouter(on_message=lambda msg: received.append(msg))
    app.include_router(tg.router, prefix="/telegram")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/telegram", json={"update_id": 300})
        assert len(received) == 0


# --- Client tests ---


@pytest.mark.asyncio
async def test_client_send_text(tg_settings):
    client = TelegramClient(tg_settings)
    await client.start()

    mock_request = httpx.Request(
        "POST", "https://api.telegram.org/bot123:ABC-TEST/sendMessage"
    )
    mock_response = httpx.Response(
        200, json={"ok": True, "result": {"message_id": 10}},
        request=mock_request,
    )

    with patch.object(client.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        result = await client.send_text(12345, "Test telegram")
        assert result["ok"] is True

    await client.stop()


@pytest.mark.asyncio
async def test_client_circuit_breaker_on_failure(tg_settings):
    from unittest.mock import MagicMock
    cb = MagicMock()
    client = TelegramClient(tg_settings, circuit_breaker=cb)
    await client.start()

    with patch.object(
        client.client,
        "post",
        new_callable=AsyncMock,
        side_effect=httpx.ConnectError("refused"),
    ):
        with pytest.raises(httpx.ConnectError):
            await client.send_text(12345, "Fail")
        cb.record_failure.assert_called_once()

    await client.stop()


@pytest.mark.asyncio
async def test_client_not_started():
    from bloque_channels.models.settings import TelegramSettings as TgS
    client = TelegramClient(TgS())
    with pytest.raises(RuntimeError, match="not started"):
        _ = client.client
