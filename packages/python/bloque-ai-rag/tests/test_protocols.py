"""Tests for LLMProvider and VectorStoreProvider protocols."""

from bloque_ai_rag.chroma.client import ChromaClient
from bloque_ai_rag.llm.ollama import OllamaClient
from bloque_ai_rag.llm.openai_compatible import OpenAICompatibleClient
from bloque_ai_rag.protocol import LLMProvider, VectorStoreProvider


def test_openai_client_satisfies_llm_protocol():
    client = OpenAICompatibleClient()
    assert isinstance(client, LLMProvider)


def test_ollama_client_satisfies_llm_protocol():
    client = OllamaClient()
    assert isinstance(client, LLMProvider)


def test_chroma_client_satisfies_vector_store_protocol():
    client = ChromaClient()
    assert isinstance(client, VectorStoreProvider)


def test_protocol_runtime_checkable_with_duck_type():
    class FakeLLM:
        async def generate(self, prompt: str, context: str = "") -> str:
            return "fake"

        async def health_check(self) -> bool:
            return True

    assert isinstance(FakeLLM(), LLMProvider)


def test_non_conforming_object_fails_protocol():
    class NotAnLLM:
        pass

    assert not isinstance(NotAnLLM(), LLMProvider)
    assert not isinstance(NotAnLLM(), VectorStoreProvider)
