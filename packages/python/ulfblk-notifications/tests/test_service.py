"""Tests for NotificationService orchestrator."""

from __future__ import annotations

from unittest.mock import AsyncMock

from ulfblk_notifications.models.notification import (
    Channel,
    DeliveryStatus,
    Notification,
)
from ulfblk_notifications.models.settings import NotificationSettings, TemplateSettings
from ulfblk_notifications.service.orchestrator import NotificationService
from ulfblk_notifications.templates.engine import TemplateEngine


async def test_notify_simple_sends_to_provider(mock_provider):
    service = NotificationService(
        providers={Channel.CONSOLE: mock_provider},
    )

    result = await service.notify_simple(
        "user@test.com", "Hello", "World", channels=[Channel.CONSOLE]
    )

    assert len(result.results) == 1
    assert result.results[0].status == DeliveryStatus.SENT
    assert result.rendered_subject == "Hello"
    assert result.rendered_body == "World"
    mock_provider.send.assert_called_once_with(
        "user@test.com", "Hello", "World", metadata=None
    )


async def test_notify_with_template(mock_provider):
    engine = TemplateEngine(TemplateSettings(use_jinja2=False))
    engine.register("welcome", subject="Hi {name}", body="Welcome {name} to {app}!")

    service = NotificationService(
        providers={Channel.CONSOLE: mock_provider},
        template_engine=engine,
    )

    notif = Notification(
        recipient="user@test.com",
        template_name="welcome",
        context={"name": "Alice", "app": "MyApp"},
        channels=[Channel.CONSOLE],
    )

    result = await service.notify(notif)

    assert result.rendered_subject == "Hi Alice"
    assert result.rendered_body == "Welcome Alice to MyApp!"
    assert result.results[0].status == DeliveryStatus.SENT


async def test_notify_unregistered_channel_returns_skipped(mock_provider):
    service = NotificationService(
        providers={Channel.CONSOLE: mock_provider},
    )

    notif = Notification(
        recipient="user@test.com",
        subject="Test",
        channels=[Channel.EMAIL],  # No EMAIL provider registered
    )

    result = await service.notify(notif)

    assert len(result.results) == 1
    assert result.results[0].status == DeliveryStatus.SKIPPED
    assert result.results[0].channel == Channel.EMAIL
    mock_provider.send.assert_not_called()


async def test_notify_failed_provider_returns_failed(mock_failing_provider):
    service = NotificationService(
        providers={Channel.WEBHOOK: mock_failing_provider},
    )

    notif = Notification(
        recipient="https://example.com/hook",
        subject="Alert",
        channels=[Channel.WEBHOOK],
    )

    result = await service.notify(notif)

    assert len(result.results) == 1
    assert result.results[0].status == DeliveryStatus.FAILED
    assert "Provider down" in result.results[0].error


async def test_notify_uses_default_channels(mock_provider):
    settings = NotificationSettings(default_channels=["console"])
    service = NotificationService(
        providers={Channel.CONSOLE: mock_provider},
        settings=settings,
    )

    notif = Notification(
        recipient="user@test.com",
        subject="Test",
        # channels is empty -> use defaults
    )

    result = await service.notify(notif)

    assert len(result.results) == 1
    assert result.results[0].status == DeliveryStatus.SENT


async def test_notify_explicit_subject_overrides_template(mock_provider):
    engine = TemplateEngine(TemplateSettings(use_jinja2=False))
    engine.register("alert", subject="Template Subject", body="Body: {msg}")

    service = NotificationService(
        providers={Channel.CONSOLE: mock_provider},
        template_engine=engine,
    )

    notif = Notification(
        recipient="admin@test.com",
        template_name="alert",
        context={"msg": "disk full"},
        channels=[Channel.CONSOLE],
        subject="OVERRIDE SUBJECT",
    )

    result = await service.notify(notif)

    assert result.rendered_subject == "OVERRIDE SUBJECT"
    assert result.rendered_body == "Body: disk full"


async def test_service_start_stop_calls_providers():
    provider_with_lifecycle = AsyncMock()
    provider_with_lifecycle.start = AsyncMock()
    provider_with_lifecycle.stop = AsyncMock()
    provider_with_lifecycle.send = AsyncMock(return_value={})
    provider_with_lifecycle.health_check = AsyncMock(return_value=True)

    service = NotificationService(
        providers={Channel.WEBHOOK: provider_with_lifecycle},
    )

    await service.start()
    provider_with_lifecycle.start.assert_called_once()

    await service.stop()
    provider_with_lifecycle.stop.assert_called_once()
