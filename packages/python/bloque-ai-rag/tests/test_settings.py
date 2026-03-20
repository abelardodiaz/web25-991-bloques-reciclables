"""Tests for RAG settings dataclasses."""

from bloque_ai_rag.models.settings import ChromaSettings, LLMSettings, RAGSettings


def test_chroma_settings_defaults():
    s = ChromaSettings()
    assert s.host == "localhost"
    assert s.port == 8000
    assert s.collection == "default"
    assert s.tenant_aware is False
    assert s.base_url == "http://localhost:8000"


def test_chroma_settings_api_base_url_override():
    s = ChromaSettings(api_base_url="https://chroma.example.com/")
    assert s.base_url == "https://chroma.example.com"


def test_llm_settings_provider_defaults():
    ds = LLMSettings(provider="deepseek")
    assert ds.get_base_url() == "https://api.deepseek.com"
    assert ds.get_model() == "deepseek-chat"

    oai = LLMSettings(provider="openai")
    assert oai.get_base_url() == "https://api.openai.com"
    assert oai.get_model() == "gpt-4o-mini"

    oll = LLMSettings(provider="ollama")
    assert oll.get_base_url() == "http://localhost:11434"
    assert oll.get_model() == "llama3.2"


def test_llm_settings_explicit_overrides():
    s = LLMSettings(
        provider="deepseek",
        api_base_url="https://custom.api.com",
        model="custom-model",
    )
    assert s.get_base_url() == "https://custom.api.com"
    assert s.get_model() == "custom-model"


def test_rag_settings_default_construction():
    s = RAGSettings()
    assert s.n_results == 5
    assert s.chroma.host == "localhost"
    assert s.llm.provider == "deepseek"
