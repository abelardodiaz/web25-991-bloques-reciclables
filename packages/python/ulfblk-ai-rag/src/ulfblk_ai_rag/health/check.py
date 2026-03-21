"""Health check utility for RAG pipeline components."""

from __future__ import annotations

from typing import Any


async def rag_health_check(
    vector_store: Any = None,
    llm: Any = None,
) -> dict[str, bool]:
    """Check health of RAG pipeline components.

    Args:
        vector_store: Object with async health_check() method.
        llm: Object with async health_check() method.

    Returns:
        Dict with component names as keys and health status as values.
    """
    result: dict[str, bool] = {}

    if vector_store is not None:
        try:
            result["vector_store"] = await vector_store.health_check()
        except Exception:
            result["vector_store"] = False

    if llm is not None:
        try:
            result["llm"] = await llm.health_check()
        except Exception:
            result["llm"] = False

    return result
