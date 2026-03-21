"""Tests for ulfblk-db migrations module."""

import os
import tempfile
from pathlib import Path

import pytest

from ulfblk_db.migrations import MigrationSettings, init_migrations, run_upgrade


class TestMigrationSettings:
    def test_defaults(self):
        settings = MigrationSettings()
        assert settings.migrations_dir == "./migrations"
        assert "postgresql" in settings.database_url

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("BLOQUE_MIGRATIONS_DIR", "/custom/path")
        settings = MigrationSettings()
        assert settings.migrations_dir == "/custom/path"

    def test_inherits_database_settings(self):
        settings = MigrationSettings(
            database_url="sqlite:///test.db",
            db_pool_size=20,
        )
        assert settings.database_url == "sqlite:///test.db"
        assert settings.db_pool_size == 20


class TestInitMigrations:
    def test_creates_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            migrations_dir = os.path.join(tmpdir, "migrations")
            settings = MigrationSettings(
                migrations_dir=migrations_dir,
                database_url="sqlite:///test.db",
            )
            result = init_migrations(settings)
            assert result == Path(migrations_dir)
            assert Path(migrations_dir).is_dir()

    def test_creates_versions_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            migrations_dir = os.path.join(tmpdir, "migrations")
            settings = MigrationSettings(
                migrations_dir=migrations_dir,
                database_url="sqlite:///test.db",
            )
            init_migrations(settings)
            assert (Path(migrations_dir) / "versions").is_dir()

    def test_creates_env_py(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            migrations_dir = os.path.join(tmpdir, "migrations")
            settings = MigrationSettings(
                migrations_dir=migrations_dir,
                database_url="sqlite:///test.db",
            )
            init_migrations(settings)
            env_path = Path(migrations_dir) / "env.py"
            assert env_path.exists()
            content = env_path.read_text()
            assert "target_metadata" in content
            assert "run_migrations_online" in content

    def test_creates_alembic_ini(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            migrations_dir = os.path.join(tmpdir, "migrations")
            settings = MigrationSettings(
                migrations_dir=migrations_dir,
                database_url="sqlite:///test.db",
            )
            init_migrations(settings)
            ini_path = Path(tmpdir) / "alembic.ini"
            assert ini_path.exists()
            content = ini_path.read_text()
            assert "sqlite:///test.db" in content

    def test_creates_script_mako(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            migrations_dir = os.path.join(tmpdir, "migrations")
            settings = MigrationSettings(
                migrations_dir=migrations_dir,
                database_url="sqlite:///test.db",
            )
            init_migrations(settings)
            mako_path = Path(migrations_dir) / "script.py.mako"
            assert mako_path.exists()

    def test_idempotent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            migrations_dir = os.path.join(tmpdir, "migrations")
            settings = MigrationSettings(
                migrations_dir=migrations_dir,
                database_url="sqlite:///test.db",
            )
            init_migrations(settings)
            # Second call should not fail
            init_migrations(settings)
            assert (Path(migrations_dir) / "env.py").exists()


class TestCLI:
    def test_help(self):
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-m", "ulfblk_db.migrations", "--help"],
            capture_output=True,
            text=True,
        )
        assert "init" in result.stdout
        assert "create" in result.stdout
        assert "upgrade" in result.stdout
        assert "downgrade" in result.stdout
