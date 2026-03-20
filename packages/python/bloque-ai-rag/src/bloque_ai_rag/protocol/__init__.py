"""Protocols for bloque-ai-rag."""

from bloque_ai_rag.protocol.llm import LLMProvider
from bloque_ai_rag.protocol.vector_store import VectorStoreProvider

__all__ = [
    "LLMProvider",
    "VectorStoreProvider",
]
