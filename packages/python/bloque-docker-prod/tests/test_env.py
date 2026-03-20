"""Tests for env module."""

from __future__ import annotations

import os

import pytest
from bloque_docker_prod.env import ProdDefaults, get_prod_defaults, load_prod_env


class TestProdDefaults:
    def test_default_postgres_url_uses_service_name(self):
        d = ProdDefaults()
        assert "@postgres:" in d.postgres_url
        assert "5432" in d.postgres_url

    def test_default_redis_url_uses_service_name(self):
        d = ProdDefaults()
        assert "@redis:" in d.redis_url

    def test_default_chromadb_url_uses_service_name(self):
        d = ProdDefaults()
        assert "chromadb:8000" in d.chromadb_url

    def test_default_app_workers(self):
        d = ProdDefaults()
        assert d.app_workers == 4

    def test_default_app_port(self):
        d = ProdDefaults()
        assert d.app_port == 8000

    def test_frozen(self):
        d = ProdDefaults()
        with pytest.raises(AttributeError):
            d.postgres_url = "other"  # type: ignore[misc]


class TestGetProdDefaults:
    def test_returns_defaults(self):
        result = get_prod_defaults()
        assert isinstance(result, ProdDefaults)
        assert result == ProdDefaults()


class TestLoadProdEnv:
    def test_sets_env_vars(self, monkeypatch):
        for var in ("DATABASE_URL", "REDIS_URL", "CHROMADB_URL", "APP_PORT", "APP_WORKERS"):
            monkeypatch.delenv(var, raising=False)

        defaults = load_prod_env()

        assert os.environ["DATABASE_URL"] == defaults.postgres_url
        assert os.environ["REDIS_URL"] == defaults.redis_url
        assert os.environ["CHROMADB_URL"] == defaults.chromadb_url
        assert os.environ["APP_PORT"] == str(defaults.app_port)
        assert os.environ["APP_WORKERS"] == str(defaults.app_workers)

    def test_no_overwrite_by_default(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "existing-url")

        load_prod_env()

        assert os.environ["DATABASE_URL"] == "existing-url"

    def test_overwrite_when_requested(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "existing-url")

        defaults = load_prod_env(overwrite=True)

        assert os.environ["DATABASE_URL"] == defaults.postgres_url

    def test_returns_defaults_instance(self, monkeypatch):
        for var in ("DATABASE_URL", "REDIS_URL", "CHROMADB_URL", "APP_PORT", "APP_WORKERS"):
            monkeypatch.delenv(var, raising=False)

        result = load_prod_env()
        assert isinstance(result, ProdDefaults)

    def test_defaults_use_docker_service_names(self):
        """Prod defaults must use Docker service names, not localhost."""
        d = ProdDefaults()
        assert "localhost" not in d.postgres_url
        assert "localhost" not in d.redis_url
        assert "localhost" not in d.chromadb_url
