"""Tests for settings override utilities."""

from ulfblk_core import BloqueSettings

from ulfblk_testing import create_test_settings, override_settings


class TestCreateTestSettings:
    def test_creates_with_overrides(self):
        settings = create_test_settings(BloqueSettings, debug=True, log_level="DEBUG")
        assert settings.debug is True
        assert settings.log_level == "DEBUG"

    def test_defaults_preserved(self):
        settings = create_test_settings(BloqueSettings, debug=True)
        assert settings.service_name == "api"
        assert settings.version == "0.1.0"


class TestOverrideSettings:
    def test_patches_and_restores(self):
        import ulfblk_testing.settings as mod

        mod._test_target = BloqueSettings()
        assert mod._test_target.debug is False

        with override_settings(
            "ulfblk_testing.settings._test_target", BloqueSettings, debug=True
        ) as s:
            assert s.debug is True
            assert mod._test_target.debug is True

        assert mod._test_target.debug is False
