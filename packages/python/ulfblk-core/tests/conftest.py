"""Shared fixtures for ulfblk-core tests."""

import pytest

from ulfblk_core.config.settings import BloqueSettings


@pytest.fixture
def default_settings():
    """BloqueSettings with all defaults."""
    return BloqueSettings()


@pytest.fixture
def custom_settings():
    """BloqueSettings with custom values."""
    return BloqueSettings(
        service_name="my-service",
        version="2.0.0",
        debug=True,
        log_level="DEBUG",
        log_json_format=True,
    )
