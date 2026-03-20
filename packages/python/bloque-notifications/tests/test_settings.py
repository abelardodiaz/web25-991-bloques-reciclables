"""Tests for notification settings."""

from bloque_notifications.models.settings import (
    NotificationSettings,
    TemplateSettings,
    WebhookProviderSettings,
)


def test_template_settings_defaults():
    s = TemplateSettings()
    assert s.template_dir == ""
    assert s.use_jinja2 is True
    assert s.autoescape is True
    assert s.tenant_aware is False


def test_webhook_settings_defaults():
    s = WebhookProviderSettings()
    assert s.timeout == 30.0
    assert s.default_url == ""
    assert s.headers == {}


def test_webhook_settings_custom():
    s = WebhookProviderSettings(
        timeout=10.0,
        default_url="https://example.com/hook",
        headers={"X-Custom": "value"},
    )
    assert s.timeout == 10.0
    assert s.default_url == "https://example.com/hook"
    assert s.headers == {"X-Custom": "value"}


def test_notification_settings_defaults():
    s = NotificationSettings()
    assert isinstance(s.templates, TemplateSettings)
    assert s.default_channels == []


def test_notification_settings_custom():
    s = NotificationSettings(
        templates=TemplateSettings(use_jinja2=False),
        default_channels=["email", "webhook"],
    )
    assert s.templates.use_jinja2 is False
    assert s.default_channels == ["email", "webhook"]
