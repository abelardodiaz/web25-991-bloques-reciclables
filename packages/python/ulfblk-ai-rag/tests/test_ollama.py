"""Tests for OllamaClient."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from ulfblk_ai_rag.llm.ollama import OllamaClient


def test_client_not_started():
    client = OllamaClient()
    with pytest.raises(RuntimeError, match="not started"):
        _ = client.client


async def test_generate_uses_ollama_format(ollama_client):
    await ollama_client.start()

    mock_request = httpx.Request("POST", "http://localhost:11434/api/chat")
    mock_response = httpx.Response(
        200,
        json={"message": {"content": "Python is a programming language."}},
        request=mock_request,
    )

    with patch.object(
        ollama_client.client, "post", new_callable=AsyncMock
    ) as mock_post:
        mock_post.return_value = mock_response
        result = await ollama_client.generate(
            "What is Python?", context="Python is a language."
        )
        assert result == "Python is a programming language."
        mock_post.assert_called_once()

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert payload["stream"] is False
        assert payload["model"] == "llama3.2"
        assert len(payload["messages"]) == 2
        assert payload["messages"][0]["role"] == "system"
        assert "options" in payload
        assert "temperature" in payload["options"]

    await ollama_client.stop()


async def test_generate_without_context(ollama_client):
    await ollama_client.start()

    mock_request = httpx.Request("POST", "http://localhost:11434/api/chat")
    mock_response = httpx.Response(
        200,
        json={"message": {"content": "Hi there!"}},
        request=mock_request,
    )

    with patch.object(
        ollama_client.client, "post", new_callable=AsyncMock
    ) as mock_post:
        mock_post.return_value = mock_response
        result = await ollama_client.generate("Hello")
        assert result == "Hi there!"

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        # No context -> only user message
        assert len(payload["messages"]) == 1
        assert payload["messages"][0]["role"] == "user"

    await ollama_client.stop()


async def test_health_check_success(ollama_client):
    await ollama_client.start()

    mock_request = httpx.Request("GET", "http://localhost:11434/api/tags")
    mock_response = httpx.Response(
        200, json={"models": []}, request=mock_request
    )

    with patch.object(
        ollama_client.client, "get", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_response
        assert await ollama_client.health_check() is True

    await ollama_client.stop()


async def test_health_check_failure(ollama_client):
    await ollama_client.start()

    with patch.object(
        ollama_client.client,
        "get",
        new_callable=AsyncMock,
        side_effect=httpx.ConnectError("refused"),
    ):
        assert await ollama_client.health_check() is False

    await ollama_client.stop()
