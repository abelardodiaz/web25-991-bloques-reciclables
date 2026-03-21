"""Tests for ChromaClient."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from ulfblk_ai_rag.chroma.client import ChromaClient
from ulfblk_ai_rag.models.settings import ChromaSettings


def test_client_not_started():
    client = ChromaClient()
    with pytest.raises(RuntimeError, match="not started"):
        _ = client.client


async def test_start_creates_client():
    client = ChromaClient()
    await client.start()
    assert client._client is not None
    await client.stop()


async def test_start_idempotent():
    client = ChromaClient()
    await client.start()
    first = client._client
    await client.start()
    assert client._client is first
    await client.stop()


async def test_external_client_not_closed():
    ext = httpx.AsyncClient()
    client = ChromaClient(http_client=ext)
    await client.start()
    await client.stop()
    assert not ext.is_closed
    await ext.aclose()


async def test_context_manager():
    async with ChromaClient() as client:
        assert client._client is not None
    assert client._client is None


def test_resolve_collection_default():
    settings = ChromaSettings(collection="my_col")
    client = ChromaClient(settings)
    assert client.resolve_collection() == "my_col"


def test_resolve_collection_override():
    client = ChromaClient()
    assert client.resolve_collection("custom") == "custom"


def test_resolve_collection_with_tenant():
    client = ChromaClient()
    assert client.resolve_collection("docs", tenant_id="acme") == "acme__docs"


def test_resolve_collection_tenant_aware_no_multitenant():
    settings = ChromaSettings(tenant_aware=True, collection="kb")
    client = ChromaClient(settings)
    # ulfblk_multitenant not installed -> no prefix
    assert client.resolve_collection() == "kb"


async def test_get_or_create_collection(chroma_client):
    await chroma_client.start()

    mock_request = httpx.Request("POST", "http://localhost:8000/api/v1/collections")
    mock_response = httpx.Response(
        200,
        json={"id": "uuid-123", "name": "test_collection"},
        request=mock_request,
    )

    with patch.object(
        chroma_client.client, "post", new_callable=AsyncMock
    ) as mock_post:
        mock_post.return_value = mock_response
        uid = await chroma_client.get_or_create_collection("test_collection")
        assert uid == "uuid-123"
        mock_post.assert_called_once()

        # Second call should use cache
        uid2 = await chroma_client.get_or_create_collection("test_collection")
        assert uid2 == "uuid-123"
        mock_post.assert_called_once()  # still once

    await chroma_client.stop()


async def test_add_documents(chroma_client):
    await chroma_client.start()
    chroma_client._collection_cache["docs"] = "uuid-456"

    mock_request = httpx.Request(
        "POST", "http://localhost:8000/api/v1/collections/uuid-456/add"
    )
    mock_response = httpx.Response(200, json=None, request=mock_request)

    with patch.object(
        chroma_client.client, "post", new_callable=AsyncMock
    ) as mock_post:
        mock_post.return_value = mock_response
        await chroma_client.add_documents(["doc1", "doc2"], "docs")
        mock_post.assert_called_once()

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert payload["documents"] == ["doc1", "doc2"]
        assert len(payload["ids"]) == 2

    await chroma_client.stop()


async def test_query(chroma_client):
    await chroma_client.start()
    chroma_client._collection_cache["kb"] = "uuid-789"

    mock_request = httpx.Request(
        "POST", "http://localhost:8000/api/v1/collections/uuid-789/query"
    )
    mock_response = httpx.Response(
        200,
        json={
            "documents": [["doc about python", "doc about java"]],
            "ids": [["id1", "id2"]],
            "distances": [[0.1, 0.5]],
            "metadatas": [[{"source": "wiki"}, {}]],
        },
        request=mock_request,
    )

    with patch.object(
        chroma_client.client, "post", new_callable=AsyncMock
    ) as mock_post:
        mock_post.return_value = mock_response
        results = await chroma_client.query("python", "kb", n_results=2)

        assert len(results) == 2
        assert results[0]["text"] == "doc about python"
        assert results[0]["id"] == "id1"
        assert results[0]["distance"] == 0.1
        assert results[0]["metadata"] == {"source": "wiki"}
        assert results[1]["text"] == "doc about java"

    await chroma_client.stop()


async def test_health_check_success(chroma_client):
    await chroma_client.start()

    mock_request = httpx.Request("GET", "http://localhost:8000/api/v1/heartbeat")
    mock_response = httpx.Response(
        200, json={"nanosecond heartbeat": 123}, request=mock_request
    )

    with patch.object(
        chroma_client.client, "get", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_response
        assert await chroma_client.health_check() is True

    await chroma_client.stop()


async def test_health_check_failure(chroma_client):
    await chroma_client.start()

    with patch.object(
        chroma_client.client,
        "get",
        new_callable=AsyncMock,
        side_effect=httpx.ConnectError("refused"),
    ):
        assert await chroma_client.health_check() is False

    await chroma_client.stop()
