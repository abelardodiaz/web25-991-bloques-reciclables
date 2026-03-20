"""Shared fixtures for bloque-notifications tests."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from bloque_notifications.models.notification import Channel
from bloque_notifications.models.settings import (
    NotificationSettings,
    TemplateSettings,
    WebhookProviderSettings,
)
from bloque_notifications.providers.console import ConsoleProvider
from bloque_notifications.service.orchestrator import NotificationService
from bloque_notifications.templates.engine import TemplateEngine  # noqa: F401


@pytest.fixture
def template_settings():
    return TemplateSettings(use_jinja2=False)


@pytest.fixture
def webhook_settings():
    return WebhookProviderSettings(
        timeout=5.0,
        default_url="https://hooks.example.com/notify",
    )


@pytest.fixture
def notification_settings(template_settings):
    return NotificationSettings(
        templates=template_settings,
        default_channels=["console"],
    )


@pytest.fixture
def template_engine(template_settings):
    return TemplateEngine(template_settings)


@pytest.fixture
def console_provider():
    return ConsoleProvider()


@pytest.fixture
def mock_provider():
    """A mock provider that satisfies NotificationProvider protocol."""
    provider = AsyncMock()
    provider.send = AsyncMock(return_value={"status": "sent"})
    provider.health_check = AsyncMock(return_value=True)
    return provider


@pytest.fixture
def mock_failing_provider():
    """A mock provider that always fails on send."""
    provider = AsyncMock()
    provider.send = AsyncMock(side_effect=RuntimeError("Provider down"))
    provider.health_check = AsyncMock(return_value=False)
    return provider


@pytest.fixture
def service(console_provider, notification_settings):
    return NotificationService(
        providers={Channel.CONSOLE: console_provider},
        settings=notification_settings,
    )
