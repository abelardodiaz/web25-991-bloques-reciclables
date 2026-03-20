"""Telegram webhook secret token verification."""

from __future__ import annotations

import hmac


def verify_telegram_secret(
    request_token: str | None, expected_token: str
) -> bool:
    """Verify the X-Telegram-Bot-Api-Secret-Token header.

    Args:
        request_token: Value from the request header (may be None).
        expected_token: The secret_token configured when setting the webhook.

    Returns:
        True if the tokens match, False otherwise.
    """
    if request_token is None:
        return False
    return hmac.compare_digest(request_token, expected_token)
