"""Tests for billing health check."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from ulfblk_billing.health.check import billing_health_check


class TestBillingHealthCheck:
    @pytest.mark.asyncio
    async def test_healthy_provider(self):
        provider = AsyncMock()
        provider.health_check = AsyncMock(return_value=True)

        result = await billing_health_check(provider)
        assert result == {"billing": True}

    @pytest.mark.asyncio
    async def test_unhealthy_provider(self):
        provider = AsyncMock()
        provider.health_check = AsyncMock(return_value=False)

        result = await billing_health_check(provider)
        assert result == {"billing": False}

    @pytest.mark.asyncio
    async def test_no_provider(self):
        result = await billing_health_check()
        assert result == {"billing": False}

    @pytest.mark.asyncio
    async def test_provider_exception(self):
        provider = AsyncMock()
        provider.health_check = AsyncMock(side_effect=Exception("down"))

        result = await billing_health_check(provider)
        assert result == {"billing": False}
