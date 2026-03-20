"""Tests for notification models."""

from bloque_notifications.models.notification import (
    Channel,
    ChannelResult,
    DeliveryStatus,
    Notification,
    NotificationResult,
    Priority,
)


def test_channel_enum_values():
    assert Channel.EMAIL == "email"
    assert Channel.WEBHOOK == "webhook"
    assert Channel.PUSH == "push"
    assert Channel.CONSOLE == "console"


def test_priority_enum_values():
    assert Priority.LOW == "low"
    assert Priority.NORMAL == "normal"
    assert Priority.HIGH == "high"
    assert Priority.CRITICAL == "critical"


def test_delivery_status_enum_values():
    assert DeliveryStatus.SENT == "sent"
    assert DeliveryStatus.FAILED == "failed"
    assert DeliveryStatus.SKIPPED == "skipped"


def test_notification_defaults():
    notif = Notification(recipient="user@test.com")
    assert notif.recipient == "user@test.com"
    assert notif.template_name == ""
    assert notif.context == {}
    assert notif.channels == []
    assert notif.priority == Priority.NORMAL
    assert notif.subject == ""
    assert notif.metadata == {}
    assert notif.tenant_id is None


def test_notification_result_has_uuid():
    result = NotificationResult()
    assert result.notification_id
    assert len(result.notification_id) == 36  # UUID format
    assert result.results == []
    assert result.rendered_subject == ""
    assert result.rendered_body == ""
    assert result.timestamp is not None


def test_channel_result_frozen():
    cr = ChannelResult(
        channel=Channel.EMAIL,
        status=DeliveryStatus.SENT,
        detail={"message_id": "abc"},
    )
    assert cr.channel == Channel.EMAIL
    assert cr.status == DeliveryStatus.SENT
    assert cr.detail == {"message_id": "abc"}
    assert cr.error == ""
