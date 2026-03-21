"""Tests for CalendarSettings."""

from ulfblk_core import BloqueSettings

from ulfblk_calendar import CalendarSettings


class TestCalendarSettings:
    def test_defaults(self):
        settings = CalendarSettings()
        assert settings.google_credentials_path == ""
        assert settings.google_calendar_id == ""
        assert settings.timezone == "UTC"

    def test_inherits_bloque_settings(self):
        assert issubclass(CalendarSettings, BloqueSettings)

    def test_has_base_fields(self):
        settings = CalendarSettings()
        assert hasattr(settings, "service_name")
        assert hasattr(settings, "debug")

    def test_env_prefix(self, monkeypatch):
        monkeypatch.setenv("BLOQUE_CALENDAR_TIMEZONE", "America/New_York")
        settings = CalendarSettings()
        assert settings.timezone == "America/New_York"

    def test_google_credentials_override(self, monkeypatch):
        monkeypatch.setenv("BLOQUE_CALENDAR_GOOGLE_CREDENTIALS_PATH", "/tmp/creds.json")
        settings = CalendarSettings()
        assert settings.google_credentials_path == "/tmp/creds.json"

    def test_google_calendar_id_override(self, monkeypatch):
        monkeypatch.setenv("BLOQUE_CALENDAR_GOOGLE_CALENDAR_ID", "primary")
        settings = CalendarSettings()
        assert settings.google_calendar_id == "primary"

    def test_extra_fields_ignored(self):
        settings = CalendarSettings(nonexistent_field="should_not_fail")
        assert not hasattr(settings, "nonexistent_field")
