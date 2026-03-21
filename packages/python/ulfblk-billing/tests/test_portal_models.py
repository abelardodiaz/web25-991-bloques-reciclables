"""Tests for portal data models."""

import pytest
from ulfblk_billing.models.portal import PortalCreate, PortalData


class TestPortalCreate:
    def test_minimal(self):
        p = PortalCreate(customer_id="cus_123")
        assert p.customer_id == "cus_123"
        assert p.return_url == ""

    def test_with_return_url(self):
        p = PortalCreate(customer_id="cus_123", return_url="https://app.example.com")
        assert p.return_url == "https://app.example.com"


class TestPortalData:
    def test_frozen(self):
        p = PortalData(id="bps_123", url="https://billing.stripe.com/xxx")
        assert p.url == "https://billing.stripe.com/xxx"
        with pytest.raises(AttributeError):
            p.id = "bps_999"  # type: ignore[misc]
