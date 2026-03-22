"""Tests for BloqueSettings configuration."""


from ulfblk_core.config.settings import BloqueSettings


def test_default_values(default_settings):
    assert default_settings.service_name == "api"
    assert default_settings.version == "0.1.0"
    assert default_settings.debug is False
    assert default_settings.log_level == "INFO"
    assert default_settings.log_json_format is False


def test_custom_values(custom_settings):
    assert custom_settings.service_name == "my-service"
    assert custom_settings.version == "2.0.0"
    assert custom_settings.debug is True
    assert custom_settings.log_level == "DEBUG"
    assert custom_settings.log_json_format is True


def test_env_var_override(monkeypatch):
    monkeypatch.setenv("BLOQUE_SERVICE_NAME", "from-env")
    monkeypatch.setenv("BLOQUE_DEBUG", "true")
    monkeypatch.setenv("BLOQUE_LOG_LEVEL", "WARNING")
    settings = BloqueSettings()
    assert settings.service_name == "from-env"
    assert settings.debug is True
    assert settings.log_level == "WARNING"


def test_subclass():
    class MySettings(BloqueSettings):
        database_url: str = "sqlite:///test.db"

    s = MySettings()
    assert s.service_name == "api"
    assert s.database_url == "sqlite:///test.db"


def test_extra_fields_ignored(monkeypatch):
    monkeypatch.setenv("BLOQUE_UNKNOWN_FIELD", "whatever")
    settings = BloqueSettings()
    assert not hasattr(settings, "unknown_field")


def test_subclass_env_override(monkeypatch):
    class MySettings(BloqueSettings):
        database_url: str = "sqlite:///test.db"

    monkeypatch.setenv("BLOQUE_DATABASE_URL", "postgresql://localhost/prod")
    s = MySettings()
    assert s.database_url == "postgresql://localhost/prod"
