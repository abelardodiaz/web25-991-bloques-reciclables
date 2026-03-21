"""Tests for SchedulingSettings."""

from ulfblk_core import BloqueSettings

from ulfblk_scheduling import SchedulingSettings


class TestSchedulingSettings:
    def test_defaults(self):
        settings = SchedulingSettings()
        assert settings.default_duration_minutes == 30
        assert settings.min_advance_hours == 1
        assert settings.max_advance_days == 60
        assert settings.buffer_minutes == 0
        assert settings.timezone == "UTC"

    def test_inherits_bloque_settings(self):
        assert issubclass(SchedulingSettings, BloqueSettings)
        settings = SchedulingSettings()
        assert hasattr(settings, "service_name")
        assert hasattr(settings, "debug")

    def test_env_var_override(self, monkeypatch):
        monkeypatch.setenv("BLOQUE_SCHEDULING_DEFAULT_DURATION_MINUTES", "60")
        settings = SchedulingSettings()
        assert settings.default_duration_minutes == 60

    def test_timezone_override(self, monkeypatch):
        monkeypatch.setenv("BLOQUE_SCHEDULING_TIMEZONE", "America/New_York")
        settings = SchedulingSettings()
        assert settings.timezone == "America/New_York"

    def test_buffer_override(self, monkeypatch):
        monkeypatch.setenv("BLOQUE_SCHEDULING_BUFFER_MINUTES", "15")
        settings = SchedulingSettings()
        assert settings.buffer_minutes == 15

    def test_advance_limits_override(self, monkeypatch):
        monkeypatch.setenv("BLOQUE_SCHEDULING_MIN_ADVANCE_HOURS", "2")
        monkeypatch.setenv("BLOQUE_SCHEDULING_MAX_ADVANCE_DAYS", "90")
        settings = SchedulingSettings()
        assert settings.min_advance_hours == 2
        assert settings.max_advance_days == 90

    def test_extra_fields_ignored(self):
        settings = SchedulingSettings(nonexistent_field="should_not_fail")
        assert not hasattr(settings, "nonexistent_field")
