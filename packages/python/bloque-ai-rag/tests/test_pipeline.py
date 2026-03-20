"""Tests for RAGPipeline."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from bloque_ai_rag.models.response import RAGResponse
from bloque_ai_rag.models.settings import RAGSettings
from bloque_ai_rag.pipeline.rag import RAGPipeline, _create_llm_client


def test_factory_creates_openai_for_deepseek():
    from bloque_ai_rag.llm.openai_compatible import OpenAICompatibleClient

    settings = RAGSettings()
    settings.llm.provider = "deepseek"
    client = _create_llm_client(settings)
    assert isinstance(client, OpenAICompatibleClient)


def test_factory_creates_openai_for_openai():
    from bloque_ai_rag.llm.openai_compatible import OpenAICompatibleClient

    settings = RAGSettings()
    settings.llm.provider = "openai"
    client = _create_llm_client(settings)
    assert isinstance(client, OpenAICompatibleClient)


def test_factory_creates_ollama_for_ollama():
    from bloque_ai_rag.llm.ollama import OllamaClient

    settings = RAGSettings()
    settings.llm.provider = "ollama"
    client = _create_llm_client(settings)
    assert isinstance(client, OllamaClient)


def test_factory_raises_for_unknown_provider():
    settings = RAGSettings()
    settings.llm.provider = "unknown"
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        _create_llm_client(settings)


async def test_respond_orchestrates_full_pipeline():
    mock_vector_store = AsyncMock()
    mock_vector_store.resolve_collection = MagicMock(return_value="test_col")
    mock_vector_store.query = AsyncMock(
        return_value=[
            {"text": "FastAPI is fast.", "id": "d1", "distance": 0.1, "metadata": {}},
            {"text": "It uses async.", "id": "d2", "distance": 0.3, "metadata": {}},
        ]
    )

    mock_llm = AsyncMock()
    mock_llm.generate = AsyncMock(return_value="FastAPI is a fast async framework.")

    pipeline = RAGPipeline(
        collection="kb",
        llm_provider="deepseek",
        vector_store=mock_vector_store,
        llm=mock_llm,
    )
    await pipeline.start()

    response = await pipeline.respond("What is FastAPI?")

    assert isinstance(response, RAGResponse)
    assert response.answer == "FastAPI is a fast async framework."
    assert len(response.contexts) == 2
    assert response.contexts[0].text == "FastAPI is fast."
    assert response.collection == "test_col"

    mock_vector_store.query.assert_called_once()
    mock_llm.generate.assert_called_once()

    # Verify context was passed to LLM
    call_args = mock_llm.generate.call_args
    assert "FastAPI is fast." in call_args.kwargs.get("context", call_args[1].get("context", ""))

    await pipeline.stop()


async def test_ingest_delegates_to_vector_store():
    mock_vector_store = AsyncMock()
    mock_vector_store.resolve_collection = MagicMock(return_value="kb")
    mock_llm = AsyncMock()

    pipeline = RAGPipeline(
        collection="kb",
        llm_provider="deepseek",
        vector_store=mock_vector_store,
        llm=mock_llm,
    )
    await pipeline.start()

    await pipeline.ingest(["doc1", "doc2"], ids=["id1", "id2"])

    mock_vector_store.add_documents.assert_called_once_with(
        ["doc1", "doc2"], "kb", ids=["id1", "id2"], metadatas=None
    )

    await pipeline.stop()


async def test_respond_with_tenant_id():
    mock_vector_store = AsyncMock()
    mock_vector_store.resolve_collection = MagicMock(return_value="acme__kb")
    mock_vector_store.query = AsyncMock(return_value=[])
    mock_llm = AsyncMock()
    mock_llm.generate = AsyncMock(return_value="No context available.")

    pipeline = RAGPipeline(
        collection="kb",
        llm_provider="deepseek",
        vector_store=mock_vector_store,
        llm=mock_llm,
    )
    await pipeline.start()

    response = await pipeline.respond("test", tenant_id="acme")
    assert response.collection == "acme__kb"
    mock_vector_store.resolve_collection.assert_called_with("kb", tenant_id="acme")

    await pipeline.stop()


async def test_pipeline_context_manager():
    mock_vector_store = AsyncMock()
    mock_llm = AsyncMock()

    pipeline = RAGPipeline(
        collection="kb",
        vector_store=mock_vector_store,
        llm=mock_llm,
    )

    async with pipeline:
        mock_vector_store.start.assert_called_once()
        mock_llm.start.assert_called_once()
