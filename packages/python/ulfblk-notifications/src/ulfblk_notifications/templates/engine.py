"""Template engine with Jinja2 optional support."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from ulfblk_notifications.models.settings import TemplateSettings

logger = logging.getLogger(__name__)


@dataclass
class _Template:
    """Internal template storage."""

    subject: str = ""
    body: str = ""


class TemplateEngine:
    """Render notification templates.

    Uses Jinja2 when available and enabled, otherwise falls back
    to ``str.format_map()`` for simple ``{variable}`` placeholders.

    Args:
        settings: Template engine configuration.

    Example:
        engine = TemplateEngine()
        engine.register("welcome", subject="Hi {name}", body="Welcome, {name}!")
        subject, body = engine.render("welcome", {"name": "Alice"})
    """

    def __init__(self, settings: TemplateSettings | None = None) -> None:
        self.settings = settings or TemplateSettings()
        self._templates: dict[str, _Template] = {}
        self._jinja_env: Any | None = None
        self._jinja_available = False

        if self.settings.use_jinja2:
            self._init_jinja2()

    def _init_jinja2(self) -> None:
        """Try to initialize Jinja2 environment."""
        try:
            from jinja2 import Environment, FileSystemLoader, select_autoescape

            loaders: dict[str, Any] = {}
            if self.settings.template_dir:
                loaders["loader"] = FileSystemLoader(self.settings.template_dir)
            if self.settings.autoescape:
                loaders["autoescape"] = select_autoescape(
                    default_for_string=True, default=True
                )

            self._jinja_env = Environment(**loaders)
            self._jinja_available = True
            logger.debug("Jinja2 template engine initialized")
        except ImportError:
            logger.info(
                "Jinja2 not installed. Using str.format_map() fallback. "
                "Install with: uv add ulfblk-notifications[templates]"
            )
            self._jinja_available = False

    def register(
        self,
        name: str,
        *,
        subject: str = "",
        body: str = "",
        tenant_id: str | None = None,
    ) -> None:
        """Register a template by name.

        Args:
            name: Template identifier.
            subject: Subject template string.
            body: Body template string.
            tenant_id: Optional tenant prefix. If None and tenant_aware,
                resolves from ulfblk_multitenant context.
        """
        effective_tenant = tenant_id
        if effective_tenant is None and self.settings.tenant_aware:
            effective_tenant = self._resolve_tenant()

        key = f"{effective_tenant}__{name}" if effective_tenant else name
        self._templates[key] = _Template(subject=subject, body=body)
        logger.debug("Registered template %r", key)

    def render(
        self,
        template_name: str,
        context: dict[str, Any],
        *,
        tenant_id: str | None = None,
    ) -> tuple[str, str]:
        """Render a registered template.

        Args:
            template_name: Name of the registered template.
            context: Variables for rendering.
            tenant_id: Explicit tenant. If None and tenant_aware,
                resolves from ulfblk_multitenant context.

        Returns:
            Tuple of (rendered_subject, rendered_body).

        Raises:
            KeyError: If the template is not registered.
        """
        effective_tenant = tenant_id
        if effective_tenant is None and self.settings.tenant_aware:
            effective_tenant = self._resolve_tenant()

        key = f"{effective_tenant}__{template_name}" if effective_tenant else template_name
        template = self._templates.get(key)

        if template is None:
            raise KeyError(
                f"Template {key!r} not registered. "
                f"Available: {list(self._templates.keys())}"
            )

        rendered_subject = self.render_string(template.subject, context)
        rendered_body = self.render_string(template.body, context)
        return rendered_subject, rendered_body

    def render_string(self, template_str: str, context: dict[str, Any]) -> str:
        """Render a single template string.

        Uses Jinja2 if available and enabled, otherwise str.format_map().

        Args:
            template_str: Template string with placeholders.
            context: Variables for rendering.

        Returns:
            Rendered string.
        """
        if not template_str:
            return ""

        if self._jinja_available and self._jinja_env is not None:
            jinja_template = self._jinja_env.from_string(template_str)
            return jinja_template.render(context)

        return template_str.format_map(context)

    @staticmethod
    def _resolve_tenant() -> str | None:
        """Try to read tenant from ulfblk_multitenant context."""
        try:
            from ulfblk_multitenant.context import get_current_tenant

            ctx = get_current_tenant()
            return ctx.tenant_id if ctx else None
        except ImportError:
            return None
