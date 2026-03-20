"""Tests for aggregate channel health check."""

from unittest.mock import AsyncMock

import pytest
from bloque_channels.health.check import channels_health_check


@pytest.mark.asyncio
async def test_all_healthy():
    ch1 = AsyncMock()
    ch1.health_check.return_value = True
    ch2 = AsyncMock()
    ch2.health_check.return_value = True

    result = await channels_health_check({"whatsapp": ch1, "telegram": ch2})
    assert result == {"whatsapp": True, "telegram": True}


@pytest.mark.asyncio
async def test_mixed_health():
    ch1 = AsyncMock()
    ch1.health_check.return_value = True
    ch2 = AsyncMock()
    ch2.health_check.return_value = False

    result = await channels_health_check({"whatsapp": ch1, "telegram": ch2})
    assert result == {"whatsapp": True, "telegram": False}


@pytest.mark.asyncio
async def test_health_check_exception():
    ch1 = AsyncMock()
    ch1.health_check.side_effect = Exception("connection error")

    result = await channels_health_check({"broken": ch1})
    assert result == {"broken": False}
