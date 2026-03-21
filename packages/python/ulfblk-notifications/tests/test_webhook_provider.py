"""Tests for WebhookProvider."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from ulfblk_notifications.models.settings import WebhookProviderSettings
from ulfblk_notifications.providers.webhook import WebhookProvider


async def test_start_creates_client():
    provider = WebhookProvider()
    assert provider._client is None

    await provider.start()
    assert provider._client is not None

    await provider.stop()
    assert provider._client is None


async def test_start_idempotent_with_external_client():
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    provider = WebhookProvider(http_client=mock_client)

    await provider.start()
    assert provider._client is mock_client

    await provider.stop()
    # External client is NOT closed
    assert provider._client is mock_client
    mock_client.aclose.assert_not_called()


async def test_client_property_raises_when_not_started():
    provider = WebhookProvider()
    with pytest.raises(RuntimeError, match="not started"):
        _ = provider.client


async def test_send_posts_json():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '{"ok": true}'
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post = AsyncMock(return_value=mock_response)

    provider = WebhookProvider(http_client=mock_client)

    result = await provider.send(
        "https://example.com/hook",
        "Alert",
        "Server down",
        metadata={"severity": "high"},
    )

    assert result["status_code"] == 200
    mock_client.post.assert_called_once()

    call_kwargs = mock_client.post.call_args
    assert call_kwargs[1]["json"]["subject"] == "Alert"
    assert call_kwargs[1]["json"]["body"] == "Server down"
    assert call_kwargs[1]["json"]["metadata"]["severity"] == "high"


async def test_send_raises_without_url():
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    provider = WebhookProvider(
        settings=WebhookProviderSettings(default_url=""),
        http_client=mock_client,
    )

    with pytest.raises(ValueError, match="No recipient URL"):
        await provider.send("", "Subject", "Body")
