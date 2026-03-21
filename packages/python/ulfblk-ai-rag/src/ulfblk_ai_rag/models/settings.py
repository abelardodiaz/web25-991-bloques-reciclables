"""Configuration dataclasses for RAG pipeline components."""

from __future__ import annotations

from dataclasses import dataclass, field

# Default system prompt template for RAG
_DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful assistant. Use the following context to answer the user's question. "
    "If the context doesn't contain relevant information, say so.\n\n"
    "Context:\n{context}"
)

# Provider defaults
_PROVIDER_DEFAULTS: dict[str, dict[str, str]] = {
    "deepseek": {
        "api_base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
    },
    "openai": {
        "api_base_url": "https://api.openai.com",
        "model": "gpt-4o-mini",
    },
    "ollama": {
        "api_base_url": "http://localhost:11434",
        "model": "llama3.2",
    },
}


@dataclass
class ChromaSettings:
    """Configuration for ChromaDB connection.

    Args:
        host: ChromaDB server hostname.
        port: ChromaDB server port.
        collection: Default collection name.
        tenant_aware: Enable tenant-aware collection prefixing.
        api_base_url: Full base URL override (takes precedence over host/port).
        timeout: HTTP request timeout in seconds.
    """

    host: str = "localhost"
    port: int = 8000
    collection: str = "default"
    tenant_aware: bool = False
    api_base_url: str = ""
    timeout: float = 30.0

    @property
    def base_url(self) -> str:
        """Resolve the base URL for ChromaDB REST API."""
        if self.api_base_url:
            return self.api_base_url.rstrip("/")
        return f"http://{self.host}:{self.port}"


@dataclass
class LLMSettings:
    """Configuration for LLM provider.

    Args:
        provider: LLM provider name ("deepseek", "openai", "ollama").
        api_key: API key for the provider (not needed for ollama).
        api_base_url: Base URL override. Defaults per provider if empty.
        model: Model name override. Defaults per provider if empty.
        temperature: Sampling temperature.
        max_tokens: Maximum tokens in response.
        timeout: HTTP request timeout in seconds.
        system_prompt: System prompt template. Must contain {context} placeholder.
    """

    provider: str = "deepseek"
    api_key: str = ""
    api_base_url: str = ""
    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 1024
    timeout: float = 60.0
    system_prompt: str = _DEFAULT_SYSTEM_PROMPT

    def get_base_url(self) -> str:
        """Resolve base URL with provider defaults."""
        if self.api_base_url:
            return self.api_base_url.rstrip("/")
        defaults = _PROVIDER_DEFAULTS.get(self.provider, {})
        return defaults.get("api_base_url", "http://localhost:11434")

    def get_model(self) -> str:
        """Resolve model name with provider defaults."""
        if self.model:
            return self.model
        defaults = _PROVIDER_DEFAULTS.get(self.provider, {})
        return defaults.get("model", "llama3.2")


@dataclass
class RAGSettings:
    """Top-level configuration for the RAG pipeline.

    Args:
        chroma: ChromaDB connection settings.
        llm: LLM provider settings.
        n_results: Number of context documents to retrieve per query.
    """

    chroma: ChromaSettings = field(default_factory=ChromaSettings)
    llm: LLMSettings = field(default_factory=LLMSettings)
    n_results: int = 5
