"""Tests for health module."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from ulfblk_docker_prod.health import (
    _check_http,
    _check_tcp,
    check_services,
    wait_for_services,
)


class TestCheckTcp:
    async def test_successful_connection(self):
        mock_writer = AsyncMock()
        mock_writer.close = lambda: None
        mock_writer.wait_closed = AsyncMock()

        with patch("ulfblk_docker_prod.health.asyncio.open_connection") as mock_conn:
            mock_conn.return_value = (AsyncMock(), mock_writer)
            result = await _check_tcp("postgres", 5432, timeout=1.0)

        assert result is True

    async def test_connection_refused(self):
        with patch("ulfblk_docker_prod.health.asyncio.open_connection") as mock_conn:
            mock_conn.side_effect = OSError("Connection refused")
            result = await _check_tcp("postgres", 5432, timeout=1.0)

        assert result is False

    async def test_connection_timeout(self):
        with patch("ulfblk_docker_prod.health.asyncio.wait_for") as mock_wait:
            mock_wait.side_effect = TimeoutError()
            result = await _check_tcp("postgres", 5432, timeout=0.1)

        assert result is False


class TestCheckHttp:
    async def test_healthy_endpoint(self):
        mock_response = AsyncMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("ulfblk_docker_prod.health.httpx.AsyncClient", return_value=mock_client):
            result = await _check_http("http://app:8000/health", timeout=1.0)

        assert result is True

    async def test_server_error(self):
        mock_response = AsyncMock()
        mock_response.status_code = 500

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("ulfblk_docker_prod.health.httpx.AsyncClient", return_value=mock_client):
            result = await _check_http("http://app:8000/health", timeout=1.0)

        assert result is False

    async def test_connection_error(self):
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("ulfblk_docker_prod.health.httpx.AsyncClient", return_value=mock_client):
            result = await _check_http("http://app:8000/health", timeout=1.0)

        assert result is False


class TestCheckServices:
    async def test_all_healthy(self):
        with (
            patch("ulfblk_docker_prod.health._check_tcp", return_value=True),
            patch("ulfblk_docker_prod.health._check_http", return_value=True),
        ):
            result = await check_services(chromadb_url="http://chromadb:8000")

        assert result == {
            "postgres": True,
            "redis": True,
            "app": True,
            "nginx": True,
            "chromadb": True,
        }

    async def test_includes_app_and_nginx(self):
        with (
            patch("ulfblk_docker_prod.health._check_tcp", return_value=True),
            patch("ulfblk_docker_prod.health._check_http", return_value=True),
        ):
            result = await check_services()

        assert "app" in result
        assert "nginx" in result

    async def test_postgres_down(self):
        async def mock_tcp(host, port, timeout):
            return port != 5432

        with (
            patch("ulfblk_docker_prod.health._check_tcp", side_effect=mock_tcp),
            patch("ulfblk_docker_prod.health._check_http", return_value=True),
        ):
            result = await check_services()

        assert result["postgres"] is False
        assert result["redis"] is True

    async def test_without_chromadb(self):
        with (
            patch("ulfblk_docker_prod.health._check_tcp", return_value=True),
            patch("ulfblk_docker_prod.health._check_http", return_value=True),
        ):
            result = await check_services()

        assert "chromadb" not in result
        assert result == {"postgres": True, "redis": True, "app": True, "nginx": True}


class TestWaitForServices:
    async def test_immediately_healthy(self):
        with (
            patch("ulfblk_docker_prod.health._check_tcp", return_value=True),
            patch("ulfblk_docker_prod.health._check_http", return_value=True),
        ):
            result = await wait_for_services(max_wait=5.0)

        assert result == {"postgres": True, "redis": True, "app": True, "nginx": True}

    async def test_becomes_healthy(self):
        call_count = 0

        async def flaky_check(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return call_count > 4

        with (
            patch("ulfblk_docker_prod.health._check_tcp", side_effect=flaky_check),
            patch("ulfblk_docker_prod.health._check_http", side_effect=flaky_check),
        ):
            result = await wait_for_services(
                max_wait=10.0,
                check_interval=0.1,
            )

        assert all(result.values())

    async def test_timeout_raises(self):
        with (
            patch("ulfblk_docker_prod.health._check_tcp", return_value=False),
            patch("ulfblk_docker_prod.health._check_http", return_value=False),
        ):
            with pytest.raises(TimeoutError, match="Services not ready"):
                await wait_for_services(max_wait=0.3, check_interval=0.1)

    async def test_selective_services(self):
        async def only_redis(host, port, timeout):
            return port == 6379

        with (
            patch("ulfblk_docker_prod.health._check_tcp", side_effect=only_redis),
            patch("ulfblk_docker_prod.health._check_http", return_value=False),
        ):
            result = await wait_for_services(
                services=["redis"],
                max_wait=5.0,
            )

        assert result["redis"] is True
