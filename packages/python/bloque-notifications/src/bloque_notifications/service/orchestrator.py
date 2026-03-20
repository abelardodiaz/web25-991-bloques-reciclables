"""Notification orchestrator service."""

from __future__ import annotations

import logging
from typing import Any

from bloque_notifications.models.notification import (
    Channel,
    ChannelResult,
    DeliveryStatus,
    Notification,
    NotificationResult,
)
from bloque_notifications.models.settings import NotificationSettings
from bloque_notifications.templates.engine import TemplateEngine

logger = logging.getLogger(__name__)


class NotificationService:
    """Orchestrate notification delivery across multiple channels.

    Renders templates, routes to registered providers, and collects
    per-channel delivery results.

    Args:
        providers: Mapping of Channel -> provider instance (duck-typed).
        settings: Service configuration.
        template_engine: Optional pre-configured template engine.

    Example:
        service = NotificationService(
            providers={Channel.CONSOLE: ConsoleProvider()},
        )
        async with service:
            result = await service.notify_simple(
                "admin@example.com", "Alert", "Server restarted"
            )
    """

    def __init__(
        self,
        providers: dict[Channel, Any] | None = None,
        *,
        settings: NotificationSettings | None = None,
        template_engine: TemplateEngine | None = None,
    ) -> None:
        self.settings = settings or NotificationSettings()
        self._providers: dict[Channel, Any] = providers or {}
        self._template_engine = template_engine

    @property
    def template_engine(self) -> TemplateEngine:
        """Get or lazily create the template engine."""
        if self._template_engine is None:
            self._template_engine = TemplateEngine(self.settings.templates)
        return self._template_engine

    async def start(self) -> None:
        """Start all providers that have a start() method."""
        for channel, provider in self._providers.items():
            if hasattr(provider, "start"):
                await provider.start()
                logger.debug("Started provider for %s", channel)

    async def stop(self) -> None:
        """Stop all providers that have a stop() method."""
        for channel, provider in self._providers.items():
            if hasattr(provider, "stop"):
                await provider.stop()
                logger.debug("Stopped provider for %s", channel)

    async def notify(self, notification: Notification) -> NotificationResult:
        """Process a notification: render template and deliver to channels.

        Steps:
            1. Determine target channels (notification or service defaults).
            2. Render template if template_name is set.
            3. Route to each channel's provider.
            4. Collect and return results.

        Args:
            notification: The notification request.

        Returns:
            NotificationResult with per-channel outcomes.
        """
        # 1. Resolve channels
        channels = notification.channels
        if not channels:
            channels = [
                Channel(c) for c in self.settings.default_channels
            ]

        # 2. Render template or use explicit subject/body
        rendered_subject = notification.subject
        rendered_body = ""

        if notification.template_name:
            rendered_subject, rendered_body = self.template_engine.render(
                notification.template_name,
                notification.context,
                tenant_id=notification.tenant_id,
            )
            if notification.subject:
                rendered_subject = notification.subject

        # 3. Route to providers and collect results
        results: list[ChannelResult] = []
        for channel in channels:
            provider = self._providers.get(channel)
            if provider is None:
                results.append(
                    ChannelResult(
                        channel=channel,
                        status=DeliveryStatus.SKIPPED,
                        error=f"No provider registered for {channel.value!r}",
                    )
                )
                logger.warning("No provider for channel %s, skipping", channel)
                continue

            try:
                detail = await provider.send(
                    notification.recipient,
                    rendered_subject,
                    rendered_body,
                    metadata=notification.metadata or None,
                )
                results.append(
                    ChannelResult(
                        channel=channel,
                        status=DeliveryStatus.SENT,
                        detail=detail or {},
                    )
                )
            except Exception as exc:
                logger.error(
                    "Failed to send via %s: %s", channel, exc, exc_info=True
                )
                results.append(
                    ChannelResult(
                        channel=channel,
                        status=DeliveryStatus.FAILED,
                        error=str(exc),
                    )
                )

        return NotificationResult(
            results=results,
            rendered_subject=rendered_subject,
            rendered_body=rendered_body,
        )

    async def notify_simple(
        self,
        recipient: str,
        subject: str,
        body: str,
        *,
        channels: list[Channel] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> NotificationResult:
        """Send a simple notification without templates.

        Convenience method that bypasses template rendering entirely.

        Args:
            recipient: Target address.
            subject: Notification subject.
            body: Notification body (already rendered).
            channels: Target channels. Falls back to service defaults.
            metadata: Extra data passed to providers.

        Returns:
            NotificationResult with per-channel outcomes.
        """
        effective_channels = channels or [
            Channel(c) for c in self.settings.default_channels
        ]

        results: list[ChannelResult] = []
        for channel in effective_channels:
            provider = self._providers.get(channel)
            if provider is None:
                results.append(
                    ChannelResult(
                        channel=channel,
                        status=DeliveryStatus.SKIPPED,
                        error=f"No provider registered for {channel.value!r}",
                    )
                )
                continue

            try:
                detail = await provider.send(
                    recipient, subject, body, metadata=metadata
                )
                results.append(
                    ChannelResult(
                        channel=channel,
                        status=DeliveryStatus.SENT,
                        detail=detail or {},
                    )
                )
            except Exception as exc:
                logger.error(
                    "Failed to send via %s: %s", channel, exc, exc_info=True
                )
                results.append(
                    ChannelResult(
                        channel=channel,
                        status=DeliveryStatus.FAILED,
                        error=str(exc),
                    )
                )

        return NotificationResult(
            results=results,
            rendered_subject=subject,
            rendered_body=body,
        )

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()
