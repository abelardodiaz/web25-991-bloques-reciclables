"""Notification settings."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TemplateSettings:
    """Settings for the template engine.

    Args:
        template_dir: Filesystem path for Jinja2 FileSystemLoader.
        use_jinja2: Attempt Jinja2 rendering; falls back to str.format_map if unavailable.
        autoescape: Enable Jinja2 autoescaping (HTML safe).
        tenant_aware: Resolve tenant from ulfblk_multitenant context automatically.
    """

    template_dir: str = ""
    use_jinja2: bool = True
    autoescape: bool = True
    tenant_aware: bool = False


@dataclass
class WebhookProviderSettings:
    """Settings for the webhook provider.

    Args:
        timeout: HTTP request timeout in seconds.
        default_url: Fallback URL when recipient is not a URL.
        headers: Extra headers to include in webhook requests.
    """

    timeout: float = 30.0
    default_url: str = ""
    headers: dict[str, str] = field(default_factory=dict)


@dataclass
class NotificationSettings:
    """Top-level notification service settings.

    Args:
        templates: Template engine configuration.
        default_channels: Channels to use when notification.channels is empty.
    """

    templates: TemplateSettings = field(default_factory=TemplateSettings)
    default_channels: list[str] = field(default_factory=list)
