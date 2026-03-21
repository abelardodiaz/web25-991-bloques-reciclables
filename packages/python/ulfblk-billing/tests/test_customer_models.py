"""Tests for customer data models."""

from ulfblk_billing.models.customer import CustomerCreate, CustomerData


class TestCustomerCreate:
    def test_minimal(self):
        c = CustomerCreate(email="user@example.com")
        assert c.email == "user@example.com"
        assert c.name == ""
        assert c.metadata == {}
        assert c.tenant_id is None

    def test_full(self):
        c = CustomerCreate(
            email="user@example.com",
            name="Jane Doe",
            metadata={"plan": "pro"},
            tenant_id="tenant-a",
        )
        assert c.name == "Jane Doe"
        assert c.metadata["plan"] == "pro"
        assert c.tenant_id == "tenant-a"


class TestCustomerData:
    def test_frozen(self):
        c = CustomerData(id="cus_123", email="user@example.com")
        assert c.id == "cus_123"
        assert c.created == 0
        import pytest
        with pytest.raises(AttributeError):
            c.id = "cus_456"  # type: ignore[misc]
