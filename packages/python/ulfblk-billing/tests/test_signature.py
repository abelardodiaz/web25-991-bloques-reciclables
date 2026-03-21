"""Tests for Stripe webhook signature verification."""

import hashlib
import hmac
import time

import pytest
from ulfblk_billing.webhooks.signature import verify_stripe_signature


def _sign(payload: bytes, secret: str, timestamp: int) -> str:
    signed = f"{timestamp}.".encode() + payload
    sig = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={sig}"


class TestVerifyStripeSignature:
    def test_valid_signature(self):
        payload = b'{"id": "evt_123"}'
        secret = "whsec_test"
        ts = int(time.time())
        sig = _sign(payload, secret, ts)

        result = verify_stripe_signature(payload, sig, secret)
        assert result == ts

    def test_invalid_signature(self):
        payload = b'{"id": "evt_123"}'
        sig = "t=12345,v1=deadbeef"

        with pytest.raises(ValueError, match="Invalid webhook signature"):
            verify_stripe_signature(payload, sig, "secret", tolerance=999999)

    def test_missing_header(self):
        with pytest.raises(ValueError, match="Missing Stripe-Signature"):
            verify_stripe_signature(b"body", "", "secret")

    def test_expired_timestamp(self):
        payload = b'{"id": "evt_123"}'
        secret = "whsec_test"
        old_ts = int(time.time()) - 600
        sig = _sign(payload, secret, old_ts)

        with pytest.raises(ValueError, match="too old"):
            verify_stripe_signature(payload, sig, secret, tolerance=300)

    def test_missing_v1(self):
        with pytest.raises(ValueError, match="Missing v1 signature"):
            verify_stripe_signature(b"body", "t=12345", "secret")

    def test_missing_timestamp(self):
        with pytest.raises(ValueError, match="Missing timestamp"):
            verify_stripe_signature(b"body", "v1=abc123", "secret")
