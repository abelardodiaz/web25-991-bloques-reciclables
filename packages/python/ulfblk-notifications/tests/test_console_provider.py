"""Tests for ConsoleProvider."""

import logging

from ulfblk_notifications.providers.console import ConsoleProvider


async def test_send_returns_logged():
    provider = ConsoleProvider()
    result = await provider.send("user@test.com", "Hello", "World")
    assert result == {"status": "logged"}


async def test_send_logs_message(caplog):
    provider = ConsoleProvider()

    with caplog.at_level(logging.INFO, logger="ulfblk_notifications.console"):
        await provider.send("admin@test.com", "Alert", "Disk full", metadata={"disk": "/dev/sda1"})

    assert "admin@test.com" in caplog.text
    assert "Alert" in caplog.text
    assert "Disk full" in caplog.text
    assert "/dev/sda1" in caplog.text


async def test_health_check_always_true():
    provider = ConsoleProvider()
    assert await provider.health_check() is True
