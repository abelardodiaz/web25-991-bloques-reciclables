"""Tests for channel models."""

from datetime import UTC, datetime

from bloque_channels.models.message import (
    ChannelType,
    InboundMessage,
    OutboundMessage,
)


def test_channel_type_values():
    assert ChannelType.WHATSAPP == "whatsapp"
    assert ChannelType.TELEGRAM == "telegram"
    assert ChannelType.EMAIL == "email"


def test_inbound_message_frozen():
    msg = InboundMessage(
        channel=ChannelType.WHATSAPP,
        sender="+5215512345678",
        text="Hola",
        message_id="wamid.123",
        timestamp=datetime.now(tz=UTC),
    )
    assert msg.channel == ChannelType.WHATSAPP
    assert msg.text == "Hola"
    assert msg.tenant_id is None
    assert msg.metadata == {}
    assert msg.raw == {}


def test_outbound_message_defaults():
    msg = OutboundMessage(recipient="+5215512345678", text="Hola")
    assert msg.channel is None
    assert msg.metadata == {}
    msg.channel = ChannelType.WHATSAPP
    assert msg.channel == ChannelType.WHATSAPP
