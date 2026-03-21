"""Response dataclasses for RAG pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RAGContext:
    """A single context document retrieved from vector search.

    Args:
        text: Document text content.
        document_id: Identifier of the document in the collection.
        distance: Distance score from the query vector (lower = more similar).
        metadata: Additional metadata associated with the document.
    """

    text: str
    document_id: str = ""
    distance: float = 0.0
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RAGResponse:
    """Complete response from the RAG pipeline.

    Args:
        answer: Generated answer text from the LLM.
        contexts: List of context documents used for generation.
        collection: Name of the ChromaDB collection queried.
        model: LLM model name used for generation.
    """

    answer: str
    contexts: list[RAGContext] = field(default_factory=list)
    collection: str = ""
    model: str = ""
