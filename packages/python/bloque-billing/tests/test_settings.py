"""Tests for billing settings."""

from bloque_billing.models.settings import BillingSettings


class TestBillingSettings:
    def test_defaults(self):
        s = BillingSettings()
        assert s.api_key == ""
        assert s.webhook_secret == ""
        assert s.api_base_url == "https://api.stripe.com"
        assert s.api_version == "2024-12-18.acacia"
        assert s.timeout == 30.0
        assert s.tenant_aware is False

    def test_custom(self):
        s = BillingSettings(
            api_key="sk_live_xxx",
            webhook_secret="whsec_yyy",
            timeout=60.0,
            tenant_aware=True,
        )
        assert s.api_key == "sk_live_xxx"
        assert s.tenant_aware is True

    def test_mutable(self):
        s = BillingSettings()
        s.api_key = "sk_test_new"
        assert s.api_key == "sk_test_new"
