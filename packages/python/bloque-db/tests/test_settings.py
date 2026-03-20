"""Tests for DatabaseSettings."""

import os

from bloque_core import BloqueSettings

from bloque_db import DatabaseSettings


class TestDatabaseSettings:
    def test_defaults(self):
        settings = DatabaseSettings()
        assert settings.database_url == "postgresql+asyncpg://localhost:5432/bloquedb"
        assert settings.db_pool_size == 5
        assert settings.db_max_overflow == 10
        assert settings.db_pool_timeout == 30
        assert settings.db_pool_recycle == 1800
        assert settings.db_echo is False

    def test_inherits_bloque_settings(self):
        assert issubclass(DatabaseSettings, BloqueSettings)
        settings = DatabaseSettings()
        assert hasattr(settings, "service_name")
        assert hasattr(settings, "debug")

    def test_env_var_override(self, monkeypatch):
        monkeypatch.setenv("BLOQUE_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        settings = DatabaseSettings()
        assert settings.database_url == "sqlite+aiosqlite:///:memory:"

    def test_pool_overrides(self, monkeypatch):
        monkeypatch.setenv("BLOQUE_DB_POOL_SIZE", "20")
        monkeypatch.setenv("BLOQUE_DB_MAX_OVERFLOW", "50")
        settings = DatabaseSettings()
        assert settings.db_pool_size == 20
        assert settings.db_max_overflow == 50

    def test_echo_override(self, monkeypatch):
        monkeypatch.setenv("BLOQUE_DB_ECHO", "true")
        settings = DatabaseSettings()
        assert settings.db_echo is True

    def test_extra_fields_ignored(self):
        settings = DatabaseSettings(nonexistent_field="should_not_fail")
        assert not hasattr(settings, "nonexistent_field")
