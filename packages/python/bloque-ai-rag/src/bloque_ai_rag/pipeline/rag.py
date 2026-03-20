"""RAG pipeline orchestrator: vector search -> context building -> LLM generation."""

from __future__ import annotations

from bloque_ai_rag.chroma.client import ChromaClient
from bloque_ai_rag.llm.ollama import OllamaClient
from bloque_ai_rag.llm.openai_compatible import OpenAICompatibleClient
from bloque_ai_rag.models.response import RAGContext, RAGResponse
from bloque_ai_rag.models.settings import RAGSettings


def _create_llm_client(
    settings: RAGSettings,
) -> OpenAICompatibleClient | OllamaClient:
    """Create an LLM client based on provider setting.

    Args:
        settings: RAG settings containing LLM configuration.

    Returns:
        Appropriate LLM client instance.

    Raises:
        ValueError: If provider is not supported.
    """
    provider = settings.llm.provider.lower()
    if provider in ("deepseek", "openai"):
        return OpenAICompatibleClient(settings.llm)
    elif provider == "ollama":
        return OllamaClient(settings.llm)
    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider!r}. "
            f"Supported: 'deepseek', 'openai', 'ollama'."
        )


class RAGPipeline:
    """Orchestrates vector search and LLM generation for RAG.

    Matches the contract from docs/recetas/bot-whatsapp.md:
        rag = RAGPipeline(collection="knowledge_base", llm_provider="deepseek")
        response = await rag.respond("What is FastAPI?")

    Power users can inject custom vector_store or llm implementations
    that satisfy VectorStoreProvider / LLMProvider protocols.

    Example:
        async with RAGPipeline(collection="kb", llm_provider="deepseek") as rag:
            await rag.ingest(["FastAPI is a web framework."])
            response = await rag.respond("What is FastAPI?")
            print(response.answer)
    """

    def __init__(
        self,
        collection: str = "default",
        llm_provider: str = "deepseek",
        *,
        settings: RAGSettings | None = None,
        vector_store: ChromaClient | None = None,
        llm: OpenAICompatibleClient | OllamaClient | None = None,
    ) -> None:
        if settings is None:
            settings = RAGSettings()
            settings.llm.provider = llm_provider
        settings.chroma.collection = collection

        self.settings = settings
        self._vector_store = vector_store or ChromaClient(settings.chroma)
        self._llm = llm or _create_llm_client(settings)
        self._owns_vector_store = vector_store is None
        self._owns_llm = llm is None

    async def start(self) -> None:
        """Start underlying clients."""
        await self._vector_store.start()
        await self._llm.start()

    async def stop(self) -> None:
        """Stop underlying clients if we own them."""
        if self._owns_llm:
            await self._llm.stop()
        if self._owns_vector_store:
            await self._vector_store.stop()

    async def ingest(
        self,
        documents: list[str],
        *,
        ids: list[str] | None = None,
        metadatas: list[dict[str, str]] | None = None,
        tenant_id: str | None = None,
    ) -> None:
        """Ingest documents into the vector store.

        Args:
            documents: List of text documents to add.
            ids: Optional document IDs.
            metadatas: Optional metadata dicts.
            tenant_id: Optional tenant identifier for collection prefixing.
        """
        collection = self._vector_store.resolve_collection(
            self.settings.chroma.collection, tenant_id=tenant_id
        )
        await self._vector_store.add_documents(
            documents, collection, ids=ids, metadatas=metadatas
        )

    async def respond(
        self, query: str, *, tenant_id: str | None = None
    ) -> RAGResponse:
        """Execute the full RAG pipeline: query -> context -> generate.

        Args:
            query: User's question text.
            tenant_id: Optional tenant identifier for collection prefixing.

        Returns:
            RAGResponse with answer and retrieved contexts.
        """
        collection = self._vector_store.resolve_collection(
            self.settings.chroma.collection, tenant_id=tenant_id
        )

        # 1. Vector search
        raw_results = await self._vector_store.query(
            query, collection, n_results=self.settings.n_results
        )

        # 2. Build contexts
        contexts = [
            RAGContext(
                text=r.get("text", ""),
                document_id=r.get("id", ""),
                distance=r.get("distance", 0.0),
                metadata=r.get("metadata") or {},
            )
            for r in raw_results
        ]

        # 3. Build context string for LLM
        context_text = "\n\n---\n\n".join(ctx.text for ctx in contexts if ctx.text)

        # 4. Generate answer
        answer = await self._llm.generate(query, context=context_text)

        return RAGResponse(
            answer=answer,
            contexts=contexts,
            collection=collection,
            model=self.settings.llm.get_model(),
        )

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()
