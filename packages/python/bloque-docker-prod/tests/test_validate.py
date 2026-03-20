"""Tests for validate module."""

from __future__ import annotations

from bloque_docker_prod.validate import validate_env, validate_prod_config


class TestValidateEnv:
    def test_valid_env(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:realpass@postgres:5432/db")
        monkeypatch.setenv("REDIS_URL", "redis://:realpass@redis:6379/0")
        monkeypatch.setenv("APP_WORKERS", "4")

        result = validate_env()

        assert result.valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_missing_required_var(self, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.setenv("REDIS_URL", "redis://:pass@redis:6379/0")
        monkeypatch.setenv("APP_WORKERS", "4")

        result = validate_env()

        assert result.valid is False
        assert any("DATABASE_URL" in e for e in result.errors)

    def test_placeholder_password_warning(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://bloques:CHANGE_ME@postgres:5432/db")
        monkeypatch.setenv("REDIS_URL", "redis://:realpass@redis:6379/0")
        monkeypatch.setenv("APP_WORKERS", "4")

        result = validate_env()

        assert result.valid is True
        assert any("CHANGE_ME" in w for w in result.warnings)

    def test_dev_password_warning(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://bloques:bloques_dev@postgres:5432/db")
        monkeypatch.setenv("REDIS_URL", "redis://:realpass@redis:6379/0")
        monkeypatch.setenv("APP_WORKERS", "4")

        result = validate_env()

        assert any("bloques_dev" in w for w in result.warnings)

    def test_invalid_workers_not_integer(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@postgres:5432/db")
        monkeypatch.setenv("REDIS_URL", "redis://:pass@redis:6379/0")
        monkeypatch.setenv("APP_WORKERS", "abc")

        result = validate_env()

        assert result.valid is False
        assert any("valid integer" in e for e in result.errors)

    def test_invalid_workers_negative(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@postgres:5432/db")
        monkeypatch.setenv("REDIS_URL", "redis://:pass@redis:6379/0")
        monkeypatch.setenv("APP_WORKERS", "-1")

        result = validate_env()

        assert result.valid is False
        assert any("positive integer" in e for e in result.errors)


class TestValidateProdConfig:
    def test_valid_without_ssl(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@postgres:5432/db")
        monkeypatch.setenv("REDIS_URL", "redis://:pass@redis:6379/0")
        monkeypatch.setenv("APP_WORKERS", "4")
        monkeypatch.delenv("SSL_CERTIFICATE", raising=False)
        monkeypatch.delenv("SSL_CERTIFICATE_KEY", raising=False)

        result = validate_prod_config()

        assert result.valid is True

    def test_valid_with_full_ssl(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@postgres:5432/db")
        monkeypatch.setenv("REDIS_URL", "redis://:pass@redis:6379/0")
        monkeypatch.setenv("APP_WORKERS", "4")
        monkeypatch.setenv("SSL_CERTIFICATE", "/etc/nginx/ssl/cert.pem")
        monkeypatch.setenv("SSL_CERTIFICATE_KEY", "/etc/nginx/ssl/key.pem")

        result = validate_prod_config()

        assert result.valid is True

    def test_partial_ssl_fails(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@postgres:5432/db")
        monkeypatch.setenv("REDIS_URL", "redis://:pass@redis:6379/0")
        monkeypatch.setenv("APP_WORKERS", "4")
        monkeypatch.setenv("SSL_CERTIFICATE", "/etc/nginx/ssl/cert.pem")
        monkeypatch.delenv("SSL_CERTIFICATE_KEY", raising=False)

        result = validate_prod_config()

        assert result.valid is False
        assert any("SSL" in e for e in result.errors)

    def test_includes_env_validation_errors(self, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.setenv("REDIS_URL", "redis://:pass@redis:6379/0")
        monkeypatch.setenv("APP_WORKERS", "4")

        result = validate_prod_config()

        assert result.valid is False
        assert any("DATABASE_URL" in e for e in result.errors)
