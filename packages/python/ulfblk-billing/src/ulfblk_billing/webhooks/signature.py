"""Stripe webhook signature verification (HMAC-SHA256, stdlib only)."""

from __future__ import annotations

import hashlib
import hmac
import time


def verify_stripe_signature(
    payload: bytes,
    signature_header: str,
    webhook_secret: str,
    *,
    tolerance: int = 300,
) -> int:
    """Verify a Stripe webhook signature.

    Stripe signs webhooks with HMAC-SHA256. The Stripe-Signature header
    contains ``t=<timestamp>,v1=<signature>``.

    Steps:
        1. Parse the Stripe-Signature header for timestamp and signature.
        2. Compute HMAC-SHA256 of ``{timestamp}.{payload}`` with webhook_secret.
        3. Compare computed signature with received using constant-time compare.
        4. Check timestamp is within tolerance window.

    Args:
        payload: Raw request body bytes.
        signature_header: Value of the Stripe-Signature header.
        webhook_secret: Webhook signing secret (whsec_...).
        tolerance: Maximum age in seconds (default 300 = 5 minutes).

    Returns:
        The event timestamp (int) on success.

    Raises:
        ValueError: If the signature is missing, invalid, or expired.
    """
    if not signature_header:
        raise ValueError("Missing Stripe-Signature header")

    # 1. Parse header: t=timestamp,v1=signature
    timestamp_str = ""
    signatures: list[str] = []

    for item in signature_header.split(","):
        key_value = item.strip().split("=", 1)
        if len(key_value) != 2:
            continue
        key, value = key_value
        if key == "t":
            timestamp_str = value
        elif key == "v1":
            signatures.append(value)

    if not timestamp_str:
        raise ValueError("Missing timestamp in Stripe-Signature header")
    if not signatures:
        raise ValueError("Missing v1 signature in Stripe-Signature header")

    try:
        timestamp = int(timestamp_str)
    except ValueError as exc:
        raise ValueError("Invalid timestamp in Stripe-Signature header") from exc

    # 2. Compute expected signature
    signed_payload = f"{timestamp}.".encode() + payload
    expected = hmac.new(
        webhook_secret.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()

    # 3. Compare (at least one v1 signature must match)
    matched = any(hmac.compare_digest(expected, sig) for sig in signatures)
    if not matched:
        raise ValueError("Invalid webhook signature")

    # 4. Check tolerance
    now = int(time.time())
    if abs(now - timestamp) > tolerance:
        raise ValueError(
            f"Webhook timestamp too old: {abs(now - timestamp)}s "
            f"(tolerance: {tolerance}s)"
        )

    return timestamp
