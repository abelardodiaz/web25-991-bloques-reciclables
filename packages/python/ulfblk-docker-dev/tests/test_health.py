"""Tests for health module."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from ulfblk_docker_dev.health import (
    _check_http,
    _check_tcp,
    check_services,
    wait_for_services,
)


class TestCheckTcp:
    async def test_successful_connection(self):
        """Mock a successful TCP connection."""
        mock_writer = AsyncMock()
        mock_writer.close = lambda: None
        mock_writer.wait_closed = AsyncMock()

        with patch("ulfblk_docker_dev.health.asyncio.open_connection") as mock_conn:
            mock_conn.return_value = (AsyncMock(), mock_writer)
            result = await _check_tcp("localhost", 5432, timeout=1.0)

        assert result is True

    async def test_connection_refused(self):
        """Unreachable host returns False."""
        with patch("ulfblk_docker_dev.health.asyncio.open_connection") as mock_conn:
            mock_conn.side_effect = OSError("Connection refused")
            result = await _check_tcp("localhost", 9999, timeout=1.0)

        assert result is False

    async def test_connection_timeout(self):
        """Timeout returns False."""
        with patch("ulfblk_docker_dev.health.asyncio.wait_for") as mock_wait:
            mock_wait.side_effect = TimeoutError()
            result = await _check_tcp("localhost", 5432, timeout=0.1)

        assert result is False


class TestCheckHttp:
    async def test_healthy_endpoint(self):
        """200 response returns True."""
        mock_response = AsyncMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("ulfblk_docker_dev.health.httpx.AsyncClient", return_value=mock_client):
            result = await _check_http("http://localhost:8000/api/v1/heartbeat", timeout=1.0)

        assert result is True

    async def test_server_error(self):
        """500 response returns False."""
        mock_response = AsyncMock()
        mock_response.status_code = 500

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("ulfblk_docker_dev.health.httpx.AsyncClient", return_value=mock_client):
            result = await _check_http("http://localhost:8000/api/v1/heartbeat", timeout=1.0)

        assert result is False

    async def test_connection_error(self):
        """Connection error returns False."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("ulfblk_docker_dev.health.httpx.AsyncClient", return_value=mock_client):
            result = await _check_http("http://localhost:8000/api/v1/heartbeat", timeout=1.0)

        assert result is False


class TestCheckServices:
    async def test_all_healthy(self):
        """All services healthy returns all True."""
        with (
            patch("ulfblk_docker_dev.health._check_tcp", return_value=True),
            patch("ulfblk_docker_dev.health._check_http", return_value=True),
        ):
            result = await check_services(chromadb_url="http://localhost:8000")

        assert result == {"postgres": True, "redis": True, "chromadb": True}

    async def test_postgres_down(self):
        """PostgreSQL down shows False."""
        async def mock_tcp(host, port, timeout):
            return port != 5432

        with (
            patch("ulfblk_docker_dev.health._check_tcp", side_effect=mock_tcp),
        ):
            result = await check_services()

        assert result["postgres"] is False
        assert result["redis"] is True

    async def test_without_chromadb(self):
        """No chromadb_url means chromadb is not checked."""
        with patch("ulfblk_docker_dev.health._check_tcp", return_value=True):
            result = await check_services()

        assert "chromadb" not in result
        assert result == {"postgres": True, "redis": True}

    async def test_custom_ports(self):
        """Custom ports are forwarded to TCP checks."""
        calls = []

        async def track_tcp(host, port, timeout):
            calls.append((host, port))
            return True

        with patch("ulfblk_docker_dev.health._check_tcp", side_effect=track_tcp):
            await check_services(
                postgres_host="db.local",
                postgres_port=5433,
                redis_host="cache.local",
                redis_port=6380,
            )

        assert ("db.local", 5433) in calls
        assert ("cache.local", 6380) in calls


class TestWaitForServices:
    async def test_immediately_healthy(self):
        """If all healthy on first check, returns immediately."""
        with patch("ulfblk_docker_dev.health._check_tcp", return_value=True):
            result = await wait_for_services(max_wait=5.0)

        assert result == {"postgres": True, "redis": True}

    async def test_becomes_healthy(self):
        """Services become healthy after a few retries."""
        call_count = 0

        async def flaky_tcp(host, port, timeout):
            nonlocal call_count
            call_count += 1
            return call_count > 2

        with patch("ulfblk_docker_dev.health._check_tcp", side_effect=flaky_tcp):
            result = await wait_for_services(
                max_wait=10.0,
                check_interval=0.1,
            )

        assert result["postgres"] is True
        assert result["redis"] is True

    async def test_timeout_raises(self):
        """TimeoutError raised when services stay unhealthy."""
        with patch("ulfblk_docker_dev.health._check_tcp", return_value=False):
            with pytest.raises(TimeoutError, match="Services not ready"):
                await wait_for_services(max_wait=0.3, check_interval=0.1)

    async def test_selective_services(self):
        """Can wait for specific services only."""
        async def only_redis(host, port, timeout):
            return port == 6379

        with patch("ulfblk_docker_dev.health._check_tcp", side_effect=only_redis):
            result = await wait_for_services(
                services=["redis"],
                max_wait=5.0,
            )

        assert result["redis"] is True
        # postgres is False but we didn't wait for it
        assert result["postgres"] is False
