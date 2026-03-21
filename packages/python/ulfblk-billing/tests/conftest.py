"""Shared fixtures for ulfblk-billing tests."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from ulfblk_billing.models.settings import BillingSettings


@pytest.fixture
def settings():
    """Default billing settings for tests."""
    return BillingSettings(
        api_key="sk_test_fake_key_123",
        webhook_secret="whsec_test_secret_456",
        api_base_url="https://api.stripe.com",
        api_version="2024-12-18.acacia",
    )


@pytest.fixture
def tenant_settings():
    """Billing settings with tenant_aware enabled."""
    return BillingSettings(
        api_key="sk_test_fake_key_123",
        webhook_secret="whsec_test_secret_456",
        tenant_aware=True,
    )


@pytest.fixture
def mock_http_client():
    """Mock httpx.AsyncClient for provider tests."""
    client = AsyncMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_response.raise_for_status = MagicMock()
    client.request = AsyncMock(return_value=mock_response)
    client.aclose = AsyncMock()
    return client


def _make_stripe_signature(payload: bytes, secret: str, timestamp: int | None = None) -> str:
    """Create a valid Stripe-Signature header for testing."""
    ts = timestamp or int(time.time())
    signed_payload = f"{ts}.".encode() + payload
    sig = hmac.new(
        secret.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()
    return f"t={ts},v1={sig}"


def _make_webhook_payload(
    event_type: str = "customer.created",
    event_id: str = "evt_test_123",
    data: dict | None = None,
    created: int = 0,
) -> bytes:
    """Create a webhook event payload for testing."""
    return json.dumps({
        "id": event_id,
        "type": event_type,
        "created": created or int(time.time()),
        "data": {"object": data or {"id": "obj_123"}},
    }).encode("utf-8")


@pytest.fixture
def make_signature():
    """Fixture returning the make_stripe_signature helper function."""
    return _make_stripe_signature


@pytest.fixture
def make_payload():
    """Fixture returning the make_webhook_payload helper function."""
    return _make_webhook_payload
