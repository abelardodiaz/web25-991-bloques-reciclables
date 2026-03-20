"""Tests for rag_health_check."""

from unittest.mock import AsyncMock

from bloque_ai_rag.health.check import rag_health_check


async def test_health_check_all_healthy():
    mock_vs = AsyncMock()
    mock_vs.health_check = AsyncMock(return_value=True)
    mock_llm = AsyncMock()
    mock_llm.health_check = AsyncMock(return_value=True)

    result = await rag_health_check(vector_store=mock_vs, llm=mock_llm)
    assert result == {"vector_store": True, "llm": True}


async def test_health_check_partial_failure():
    mock_vs = AsyncMock()
    mock_vs.health_check = AsyncMock(return_value=True)
    mock_llm = AsyncMock()
    mock_llm.health_check = AsyncMock(return_value=False)

    result = await rag_health_check(vector_store=mock_vs, llm=mock_llm)
    assert result == {"vector_store": True, "llm": False}


async def test_health_check_exception_handled():
    mock_vs = AsyncMock()
    mock_vs.health_check = AsyncMock(side_effect=Exception("connection refused"))

    result = await rag_health_check(vector_store=mock_vs)
    assert result == {"vector_store": False}


async def test_health_check_no_components():
    result = await rag_health_check()
    assert result == {}
