"""Tests for StreamProducer and StreamConsumer."""

import pytest
from ulfblk_redis.streams.consumer import StreamConsumer
from ulfblk_redis.streams.models import StreamMessage
from ulfblk_redis.streams.producer import StreamProducer


@pytest.fixture
def producer(redis_manager):
    return StreamProducer(redis_manager, stream="events")


@pytest.fixture
def consumer(redis_manager):
    return StreamConsumer(
        redis_manager,
        stream="events",
        group="workers",
        consumer_name="w1",
        batch_size=10,
        block_ms=0,  # Don't block in tests
    )


class TestStreamProducer:
    async def test_publish_returns_id(self, producer):
        msg_id = await producer.publish({"action": "click", "page": "home"})
        assert msg_id is not None
        assert "-" in msg_id  # Redis stream IDs have format "timestamp-seq"

    async def test_stream_length(self, producer):
        assert await producer.stream_length() == 0
        await producer.publish({"a": "1"})
        await producer.publish({"b": "2"})
        assert await producer.stream_length() == 2

    async def test_publish_to_custom_stream(self, producer):
        msg_id = await producer.publish({"x": "1"}, stream="other")
        assert msg_id is not None
        assert await producer.stream_length(stream="other") == 1
        assert await producer.stream_length() == 0  # original stream untouched


class TestStreamConsumer:
    async def test_ensure_group_creates(self, consumer, producer):
        await producer.publish({"init": "1"})
        await consumer.ensure_group()
        # Should not raise on second call (BUSYGROUP handled)
        await consumer.ensure_group()

    async def test_read_and_ack(self, consumer, producer):
        await consumer.ensure_group()
        await producer.publish({"event": "signup"})
        messages = await consumer.read_and_ack()
        assert len(messages) == 1
        assert messages[0].data["event"] == "signup"
        assert isinstance(messages[0], StreamMessage)

    async def test_read_empty_stream(self, consumer):
        await consumer.ensure_group()
        messages = await consumer.read()
        assert messages == []

    async def test_ack_individual(self, consumer, producer):
        await consumer.ensure_group()
        await producer.publish({"task": "process"})
        messages = await consumer.read()
        assert len(messages) == 1
        await consumer.ack(messages[0].message_id)

    async def test_stream_message_fields(self, consumer, producer):
        await consumer.ensure_group()
        await producer.publish({"key": "value"})
        messages = await consumer.read()
        msg = messages[0]
        assert msg.stream == "events"
        assert msg.data["key"] == "value"
        assert "-" in msg.message_id

    async def test_multiple_messages(self, consumer, producer):
        await consumer.ensure_group()
        for i in range(5):
            await producer.publish({"seq": str(i)})
        messages = await consumer.read()
        assert len(messages) == 5

    async def test_recover_pending(self, redis_manager, producer):
        """recover_pending claims messages from other failed consumers."""
        # Consumer c1 reads but doesn't ack
        c1 = StreamConsumer(
            redis_manager, "events", "workers", "c1", block_ms=0, claim_after_ms=0,
        )
        await c1.ensure_group()
        await producer.publish({"data": "pending"})
        msgs = await c1.read()
        assert len(msgs) == 1

        # Consumer c2 recovers c1's pending messages
        c2 = StreamConsumer(
            redis_manager, "events", "workers", "c2", block_ms=0, claim_after_ms=0,
        )
        recovered = await c2.recover_pending()
        assert len(recovered) == 1
        assert recovered[0].data["data"] == "pending"
