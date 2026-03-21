"""Protocol for vector store implementations."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class VectorStoreProvider(Protocol):
    """Protocol that all vector store clients must satisfy.

    Duck-typed: any object with query, add_documents, and health_check
    can be used as a vector store without inheriting this class.
    """

    async def query(
        self, text: str, collection: str, n_results: int = 5
    ) -> list[dict[str, Any]]: ...

    async def add_documents(
        self,
        documents: list[str],
        collection: str,
        ids: list[str] | None = None,
        metadatas: list[dict[str, str]] | None = None,
    ) -> None: ...

    async def health_check(self) -> bool: ...
