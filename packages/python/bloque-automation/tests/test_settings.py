"""Tests for settings models."""

from bloque_automation.models.settings import RuleEngineSettings


class TestRuleEngineSettings:
    def test_defaults(self):
        settings = RuleEngineSettings()
        assert settings.tenant_aware is False
        assert settings.max_rules == 0
        assert settings.stop_on_rule_error is False

    def test_custom_values(self):
        settings = RuleEngineSettings(
            tenant_aware=True, max_rules=100, stop_on_rule_error=True
        )
        assert settings.tenant_aware is True
        assert settings.max_rules == 100
        assert settings.stop_on_rule_error is True

    def test_max_rules_zero_means_unlimited(self):
        settings = RuleEngineSettings(max_rules=0)
        assert settings.max_rules == 0
