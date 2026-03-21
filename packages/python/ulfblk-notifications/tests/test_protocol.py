"""Tests for NotificationProvider protocol."""

from __future__ import annotations

from typing import Any

from ulfblk_notifications.protocol.provider import NotificationProvider


class _ValidProvider:
    """A minimal valid provider."""

    async def send(
        self, recipient: str, subject: str, body: str, *, metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return {"status": "sent"}

    async def health_check(self) -> bool:
        return True


class _InvalidProvider:
    """Missing health_check method."""

    async def send(self, recipient: str, subject: str, body: str) -> dict[str, Any]:
        return {}


class _NoSendProvider:
    """Missing send method."""

    async def health_check(self) -> bool:
        return True


def test_valid_provider_satisfies_protocol():
    provider = _ValidProvider()
    assert isinstance(provider, NotificationProvider)


def test_invalid_provider_missing_health_check():
    provider = _InvalidProvider()
    assert not isinstance(provider, NotificationProvider)


def test_no_send_provider_fails_protocol():
    provider = _NoSendProvider()
    assert not isinstance(provider, NotificationProvider)


def test_console_provider_satisfies_protocol():
    from ulfblk_notifications.providers.console import ConsoleProvider

    provider = ConsoleProvider()
    assert isinstance(provider, NotificationProvider)


def test_webhook_provider_satisfies_protocol():
    from ulfblk_notifications.providers.webhook import WebhookProvider

    provider = WebhookProvider()
    assert isinstance(provider, NotificationProvider)
