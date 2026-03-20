"""Shared fixtures for bloque-ai-rag tests."""

import pytest
from bloque_ai_rag.chroma.client import ChromaClient
from bloque_ai_rag.llm.ollama import OllamaClient
from bloque_ai_rag.llm.openai_compatible import OpenAICompatibleClient
from bloque_ai_rag.models.settings import ChromaSettings, LLMSettings, RAGSettings


@pytest.fixture
def chroma_settings():
    return ChromaSettings(
        host="localhost",
        port=8000,
        collection="test_collection",
    )


@pytest.fixture
def llm_settings():
    return LLMSettings(
        provider="deepseek",
        api_key="test-key",
        model="deepseek-chat",
    )


@pytest.fixture
def ollama_settings():
    return LLMSettings(
        provider="ollama",
        model="llama3.2",
    )


@pytest.fixture
def rag_settings(chroma_settings, llm_settings):
    return RAGSettings(
        chroma=chroma_settings,
        llm=llm_settings,
        n_results=3,
    )


@pytest.fixture
def chroma_client(chroma_settings):
    return ChromaClient(chroma_settings)


@pytest.fixture
def openai_client(llm_settings):
    return OpenAICompatibleClient(llm_settings)


@pytest.fixture
def ollama_client(ollama_settings):
    return OllamaClient(ollama_settings)
