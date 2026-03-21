"""Tests for OpenAICompatibleClient."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from ulfblk_ai_rag.llm.openai_compatible import OpenAICompatibleClient


def test_client_not_started():
    client = OpenAICompatibleClient()
    with pytest.raises(RuntimeError, match="not started"):
        _ = client.client


async def test_generate_with_context(openai_client):
    await openai_client.start()

    mock_request = httpx.Request(
        "POST", "https://api.deepseek.com/v1/chat/completions"
    )
    mock_response = httpx.Response(
        200,
        json={
            "choices": [
                {"message": {"content": "FastAPI is a web framework."}}
            ]
        },
        request=mock_request,
    )

    with patch.object(
        openai_client.client, "post", new_callable=AsyncMock
    ) as mock_post:
        mock_post.return_value = mock_response
        result = await openai_client.generate(
            "What is FastAPI?", context="FastAPI is a modern web framework."
        )
        assert result == "FastAPI is a web framework."
        mock_post.assert_called_once()

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        # Should have system message with context + user message
        assert len(payload["messages"]) == 2
        assert payload["messages"][0]["role"] == "system"
        assert "FastAPI is a modern web framework." in payload["messages"][0]["content"]
        assert payload["messages"][1]["role"] == "user"

    await openai_client.stop()


async def test_generate_without_context(openai_client):
    await openai_client.start()

    mock_request = httpx.Request(
        "POST", "https://api.deepseek.com/v1/chat/completions"
    )
    mock_response = httpx.Response(
        200,
        json={"choices": [{"message": {"content": "Hello!"}}]},
        request=mock_request,
    )

    with patch.object(
        openai_client.client, "post", new_callable=AsyncMock
    ) as mock_post:
        mock_post.return_value = mock_response
        result = await openai_client.generate("Hi")
        assert result == "Hello!"

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        # No context -> no system message
        assert len(payload["messages"]) == 1
        assert payload["messages"][0]["role"] == "user"

    await openai_client.stop()


async def test_generate_sends_auth_header(llm_settings):
    client = OpenAICompatibleClient(llm_settings)
    await client.start()

    mock_request = httpx.Request(
        "POST", "https://api.deepseek.com/v1/chat/completions"
    )
    mock_response = httpx.Response(
        200,
        json={"choices": [{"message": {"content": "ok"}}]},
        request=mock_request,
    )

    with patch.object(
        client.client, "post", new_callable=AsyncMock
    ) as mock_post:
        mock_post.return_value = mock_response
        await client.generate("test")

        call_kwargs = mock_post.call_args
        headers = call_kwargs.kwargs.get("headers") or call_kwargs[1].get("headers")
        assert headers["Authorization"] == "Bearer test-key"

    await client.stop()


async def test_health_check_success(openai_client):
    await openai_client.start()

    mock_request = httpx.Request("GET", "https://api.deepseek.com/v1/models")
    mock_response = httpx.Response(
        200, json={"data": []}, request=mock_request
    )

    with patch.object(
        openai_client.client, "get", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_response
        assert await openai_client.health_check() is True

    await openai_client.stop()


async def test_health_check_failure(openai_client):
    await openai_client.start()

    with patch.object(
        openai_client.client,
        "get",
        new_callable=AsyncMock,
        side_effect=httpx.ConnectError("refused"),
    ):
        assert await openai_client.health_check() is False

    await openai_client.stop()
