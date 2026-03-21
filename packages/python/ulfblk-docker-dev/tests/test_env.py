"""Tests for env module."""

from __future__ import annotations

import os

import pytest
from ulfblk_docker_dev.env import DevDefaults, get_dev_defaults, load_dev_env


class TestDevDefaults:
    def test_default_postgres_url(self):
        d = DevDefaults()
        assert "bloques" in d.postgres_url
        assert "5432" in d.postgres_url

    def test_default_redis_url(self):
        d = DevDefaults()
        assert d.redis_url == "redis://localhost:6379/0"

    def test_default_chromadb_url(self):
        d = DevDefaults()
        assert d.chromadb_url == "http://localhost:8000"

    def test_frozen(self):
        d = DevDefaults()
        with pytest.raises(AttributeError):
            d.postgres_url = "other"  # type: ignore[misc]


class TestGetDevDefaults:
    def test_returns_defaults(self):
        result = get_dev_defaults()
        assert isinstance(result, DevDefaults)
        assert result == DevDefaults()


class TestLoadDevEnv:
    def test_sets_env_vars(self, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("REDIS_URL", raising=False)
        monkeypatch.delenv("CHROMADB_URL", raising=False)

        defaults = load_dev_env()

        assert os.environ["DATABASE_URL"] == defaults.postgres_url
        assert os.environ["REDIS_URL"] == defaults.redis_url
        assert os.environ["CHROMADB_URL"] == defaults.chromadb_url

    def test_no_overwrite_by_default(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "existing-url")

        load_dev_env()

        assert os.environ["DATABASE_URL"] == "existing-url"

    def test_overwrite_when_requested(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "existing-url")

        defaults = load_dev_env(overwrite=True)

        assert os.environ["DATABASE_URL"] == defaults.postgres_url

    def test_returns_defaults_instance(self, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("REDIS_URL", raising=False)
        monkeypatch.delenv("CHROMADB_URL", raising=False)

        result = load_dev_env()
        assert isinstance(result, DevDefaults)
