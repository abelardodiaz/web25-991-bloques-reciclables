"""Settings override utilities for testing."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, TypeVar
from unittest.mock import patch

from pydantic_settings import BaseSettings

T = TypeVar("T", bound=BaseSettings)


def create_test_settings(
    settings_cls: type[T],
    **overrides: Any,
) -> T:
    """Create a settings instance with test overrides.

    Args:
        settings_cls: The pydantic-settings class to instantiate.
        **overrides: Field values to override.

    Returns:
        Configured settings instance.

    Example::

        from ulfblk_core import BloqueSettings
        settings = create_test_settings(BloqueSettings, debug=True, log_level="DEBUG")
    """
    return settings_cls(**overrides)


@contextmanager
def override_settings(
    target: str,
    settings_cls: type[T],
    **overrides: Any,
) -> Generator[T, None, None]:
    """Context manager to temporarily replace a settings object.

    Patches the target attribute with a new settings instance.

    Args:
        target: Dot-separated import path to patch (e.g. "myapp.config.settings").
        settings_cls: The pydantic-settings class to instantiate.
        **overrides: Field values to override.

    Yields:
        The created settings instance.

    Example::

        with override_settings("myapp.config.settings", BloqueSettings, debug=True) as s:
            assert s.debug is True
    """
    instance = create_test_settings(settings_cls, **overrides)
    with patch(target, instance):
        yield instance
