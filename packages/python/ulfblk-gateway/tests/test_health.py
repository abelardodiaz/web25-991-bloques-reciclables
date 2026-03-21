"""Tests for gateway health check utility."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from ulfblk_gateway.health import gateway_health_check
from ulfblk_gateway.proxy import ProxyHandler, ProxyRoute, ProxySettings


@pytest.mark.asyncio
async def test_health_check_all_healthy():
    settings = ProxySettings(
        routes=[
            ProxyRoute(path_prefix="/api/a", upstream_url="http://svc-a:8001"),
            ProxyRoute(path_prefix="/api/b", upstream_url="http://svc-b:8002"),
        ]
    )
    handler = ProxyHandler(settings)
    await handler.start()

    with patch.object(
        handler.client,
        "get",
        new_callable=AsyncMock,
        return_value=httpx.Response(200),
    ):
        result = await gateway_health_check(handler)
        assert result["gateway"] is True
        assert result["upstream:http://svc-a:8001"] is True
        assert result["upstream:http://svc-b:8002"] is True

    await handler.stop()


@pytest.mark.asyncio
async def test_health_check_one_unhealthy():
    settings = ProxySettings(
        routes=[
            ProxyRoute(path_prefix="/api/a", upstream_url="http://svc-a:8001"),
            ProxyRoute(path_prefix="/api/b", upstream_url="http://svc-b:8002"),
        ]
    )
    handler = ProxyHandler(settings)
    await handler.start()

    async def mock_get(url, **kwargs):
        if "svc-b" in url:
            raise httpx.ConnectError("refused")
        return httpx.Response(200)

    with patch.object(handler.client, "get", side_effect=mock_get):
        result = await gateway_health_check(handler)
        assert result["gateway"] is True
        assert result["upstream:http://svc-a:8001"] is True
        assert result["upstream:http://svc-b:8002"] is False

    await handler.stop()


@pytest.mark.asyncio
async def test_health_check_deduplicates_urls():
    """Routes with same upstream URL should only be checked once."""
    settings = ProxySettings(
        routes=[
            ProxyRoute(path_prefix="/api/a", upstream_url="http://svc:8001"),
            ProxyRoute(path_prefix="/api/b", upstream_url="http://svc:8001"),
        ]
    )
    handler = ProxyHandler(settings)
    await handler.start()

    mock_get = AsyncMock(return_value=httpx.Response(200))
    with patch.object(handler.client, "get", mock_get):
        result = await gateway_health_check(handler)
        assert len(result) == 2  # "gateway" + 1 unique upstream
        assert mock_get.call_count == 1

    await handler.stop()
