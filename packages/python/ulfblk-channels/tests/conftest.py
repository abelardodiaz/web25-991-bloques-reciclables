"""Shared fixtures for ulfblk-channels tests."""

import pytest
from ulfblk_channels.models.settings import (
    EmailSettings,
    TelegramSettings,
    WhatsAppSettings,
)
from ulfblk_channels.telegram.client import TelegramClient
from ulfblk_channels.whatsapp.client import WhatsAppClient


@pytest.fixture
def wa_settings():
    return WhatsAppSettings(
        api_token="test-token",
        verify_token="test-verify",
        phone_number_id="123456789",
        api_version="v21.0",
        api_base_url="https://graph.facebook.com",
    )


@pytest.fixture
def tg_settings():
    return TelegramSettings(
        bot_token="123:ABC-TEST",
        secret_token="test-secret",
        api_base_url="https://api.telegram.org",
    )


@pytest.fixture
def email_settings():
    return EmailSettings(
        smtp_host="localhost",
        smtp_port=587,
        smtp_username="user@test.com",
        smtp_password="test-password",
        smtp_use_tls=True,
        from_address="bot@test.com",
        webhook_secret="email-secret",
    )


@pytest.fixture
def wa_client(wa_settings):
    return WhatsAppClient(wa_settings)


@pytest.fixture
def tg_client(tg_settings):
    return TelegramClient(tg_settings)
