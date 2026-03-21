"""Protocols for ulfblk-ai-rag."""

from ulfblk_ai_rag.protocol.llm import LLMProvider
from ulfblk_ai_rag.protocol.vector_store import VectorStoreProvider

__all__ = [
    "LLMProvider",
    "VectorStoreProvider",
]
