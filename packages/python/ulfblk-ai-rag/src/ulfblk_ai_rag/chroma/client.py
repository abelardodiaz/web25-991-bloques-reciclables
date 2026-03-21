"""ChromaDB client using httpx to talk to the REST API directly."""

from __future__ import annotations

import uuid
from typing import Any

import httpx

from ulfblk_ai_rag.models.settings import ChromaSettings


class ChromaClient:
    """HTTP client for ChromaDB REST API.

    Uses httpx instead of the chromadb package to avoid ~200MB of
    transitive dependencies (onnxruntime, numpy, tokenizers).
    ChromaDB handles embeddings server-side with its default function.

    Example:
        client = ChromaClient(settings)
        await client.start()
        await client.add_documents(["Hello world"], "my_collection")
        results = await client.query("hello", "my_collection")
        await client.stop()
    """

    def __init__(
        self,
        settings: ChromaSettings | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings or ChromaSettings()
        self._external_client = http_client is not None
        self._client = http_client
        self._collection_cache: dict[str, str] = {}

    async def start(self) -> None:
        """Create the httpx.AsyncClient if not provided externally."""
        if self._client is not None:
            return
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.settings.timeout, connect=10.0),
        )

    async def stop(self) -> None:
        """Close the httpx.AsyncClient if we own it."""
        if self._client is not None and not self._external_client:
            await self._client.aclose()
            self._client = None
        self._collection_cache.clear()

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the httpx client. Raises RuntimeError if not started."""
        if self._client is None:
            raise RuntimeError(
                "ChromaClient is not started. Call start() or use async with."
            )
        return self._client

    def resolve_collection(
        self, collection: str | None = None, tenant_id: str | None = None
    ) -> str:
        """Resolve collection name with optional tenant prefix.

        Resolution order for tenant_id:
          1. Explicit tenant_id parameter
          2. ulfblk_multitenant context (if tenant_aware=True and installed)
          3. No tenant prefix

        Args:
            collection: Collection name override. Defaults to settings.collection.
            tenant_id: Explicit tenant identifier.

        Returns:
            Resolved collection name, optionally prefixed with tenant_id.
        """
        name = collection or self.settings.collection

        effective_tenant = tenant_id
        if effective_tenant is None and self.settings.tenant_aware:
            effective_tenant = self._resolve_tenant()

        if effective_tenant:
            return f"{effective_tenant}__{name}"
        return name

    @staticmethod
    def _resolve_tenant() -> str | None:
        """Try to read tenant from ulfblk_multitenant context."""
        try:
            from ulfblk_multitenant.context import get_current_tenant

            ctx = get_current_tenant()
            return ctx.tenant_id if ctx else None
        except ImportError:
            return None

    async def get_or_create_collection(self, collection: str) -> str:
        """Get or create a collection, returning its UUID.

        Uses an internal cache to avoid repeated round-trips.

        Args:
            collection: Collection name.

        Returns:
            Collection UUID string.
        """
        if collection in self._collection_cache:
            return self._collection_cache[collection]

        url = f"{self.settings.base_url}/api/v1/collections"
        payload = {"name": collection, "get_or_create": True}
        response = await self.client.post(url, json=payload)
        response.raise_for_status()

        data = response.json()
        collection_id = data["id"]
        self._collection_cache[collection] = collection_id
        return collection_id

    async def add_documents(
        self,
        documents: list[str],
        collection: str,
        ids: list[str] | None = None,
        metadatas: list[dict[str, str]] | None = None,
    ) -> None:
        """Add documents to a ChromaDB collection.

        Args:
            documents: List of text documents to add.
            collection: Collection name.
            ids: Optional document IDs. Auto-generated if not provided.
            metadatas: Optional metadata dicts for each document.
        """
        collection_id = await self.get_or_create_collection(collection)

        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]

        url = f"{self.settings.base_url}/api/v1/collections/{collection_id}/add"
        payload: dict[str, Any] = {
            "ids": ids,
            "documents": documents,
        }
        if metadatas is not None:
            payload["metadatas"] = metadatas

        response = await self.client.post(url, json=payload)
        response.raise_for_status()

    async def query(
        self, text: str, collection: str, n_results: int = 5
    ) -> list[dict[str, Any]]:
        """Query a ChromaDB collection for similar documents.

        Args:
            text: Query text.
            collection: Collection name.
            n_results: Maximum number of results to return.

        Returns:
            List of result dicts with keys: text, id, distance, metadata.
        """
        collection_id = await self.get_or_create_collection(collection)

        url = f"{self.settings.base_url}/api/v1/collections/{collection_id}/query"
        payload = {
            "query_texts": [text],
            "n_results": n_results,
        }
        response = await self.client.post(url, json=payload)
        response.raise_for_status()

        data = response.json()
        results: list[dict[str, Any]] = []

        documents = (data.get("documents") or [[]])[0]
        ids = (data.get("ids") or [[]])[0]
        distances = (data.get("distances") or [[]])[0]
        metadatas = (data.get("metadatas") or [[]])[0]

        for i, doc in enumerate(documents):
            results.append({
                "text": doc,
                "id": ids[i] if i < len(ids) else "",
                "distance": distances[i] if i < len(distances) else 0.0,
                "metadata": metadatas[i] if i < len(metadatas) else {},
            })

        return results

    async def delete_collection(self, collection: str) -> None:
        """Delete a collection from ChromaDB.

        Args:
            collection: Collection name to delete.
        """
        url = f"{self.settings.base_url}/api/v1/collections/{collection}"
        response = await self.client.delete(url)
        response.raise_for_status()
        self._collection_cache.pop(collection, None)

    async def health_check(self) -> bool:
        """Check if ChromaDB is reachable via heartbeat endpoint."""
        try:
            url = f"{self.settings.base_url}/api/v1/heartbeat"
            response = await self.client.get(url, timeout=5.0)
            return response.status_code < 500
        except Exception:
            return False

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()
