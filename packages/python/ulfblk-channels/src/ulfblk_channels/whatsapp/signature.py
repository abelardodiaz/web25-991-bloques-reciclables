"""WhatsApp webhook signature verification (HMAC-SHA256)."""

from __future__ import annotations

import hashlib
import hmac


def verify_whatsapp_signature(
    payload: bytes, signature: str, app_secret: str
) -> bool:
    """Verify the X-Hub-Signature-256 header from Meta webhooks.

    Args:
        payload: Raw request body bytes.
        signature: Value of X-Hub-Signature-256 header (``sha256=<hex>``).
        app_secret: Facebook app secret for HMAC computation.

    Returns:
        True if the signature is valid, False otherwise.
    """
    if not signature.startswith("sha256="):
        return False

    expected = hmac.new(
        app_secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    received = signature[len("sha256=") :]
    return hmac.compare_digest(expected, received)
