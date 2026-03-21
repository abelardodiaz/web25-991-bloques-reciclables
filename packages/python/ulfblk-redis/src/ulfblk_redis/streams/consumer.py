"""Redis Streams consumer with consumer group support."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from ulfblk_core.logging import get_logger
from redis.exceptions import ResponseError

from ..client.manager import RedisManager
from .models import StreamMessage

logger = get_logger(__name__)


class StreamConsumer:
    """Consumes messages from a Redis Stream via consumer groups.

    Args:
        manager: Connected RedisManager.
        stream: Stream name.
        group: Consumer group name.
        consumer_name: Name of this consumer within the group.
        batch_size: Number of messages to read per call.
        block_ms: Milliseconds to block waiting for new messages.
        claim_after_ms: Claim pending messages older than this (ms).
        tenant_id: Optional tenant for key prefixing.
    """

    def __init__(
        self,
        manager: RedisManager,
        stream: str,
        group: str,
        consumer_name: str,
        batch_size: int = 10,
        block_ms: int = 5000,
        claim_after_ms: int = 60_000,
        tenant_id: str | None = None,
    ) -> None:
        self._manager = manager
        self._stream = stream
        self._group = group
        self._consumer_name = consumer_name
        self._batch_size = batch_size
        self._block_ms = block_ms
        self._claim_after_ms = claim_after_ms
        self._tenant_id = tenant_id

    @property
    def _full_stream(self) -> str:
        return self._manager.make_key(self._stream, tenant_id=self._tenant_id)

    async def ensure_group(self) -> None:
        """Create the consumer group if it doesn't exist.

        Uses MKSTREAM to create the stream if needed.
        """
        try:
            await self._manager.client.xgroup_create(
                self._full_stream,
                self._group,
                id="0",
                mkstream=True,
            )
            logger.info(
                "consumer_group_created",
                stream=self._full_stream,
                group=self._group,
            )
        except ResponseError as e:
            if "BUSYGROUP" in str(e):
                pass  # Group already exists
            else:
                raise

    async def read(self) -> list[StreamMessage]:
        """Read new messages from the consumer group."""
        results = await self._manager.client.xreadgroup(
            groupname=self._group,
            consumername=self._consumer_name,
            streams={self._full_stream: ">"},
            count=self._batch_size,
            block=self._block_ms,
        )
        return self._parse_results(results)

    async def ack(self, message_id: str) -> None:
        """Acknowledge a message as processed."""
        await self._manager.client.xack(
            self._full_stream, self._group, message_id
        )

    async def read_and_ack(self) -> list[StreamMessage]:
        """Read messages and immediately acknowledge them."""
        messages = await self.read()
        for msg in messages:
            await self.ack(msg.message_id)
        return messages

    async def recover_pending(self) -> list[StreamMessage]:
        """Claim and return pending messages from failed consumers.

        Uses XAUTOCLAIM to reclaim messages that have been idle
        longer than claim_after_ms.
        """
        result = await self._manager.client.xautoclaim(
            self._full_stream,
            self._group,
            self._consumer_name,
            min_idle_time=self._claim_after_ms,
            start_id="0-0",
            count=self._batch_size,
        )
        # xautoclaim returns (next_start_id, messages, deleted_ids)
        raw_messages = result[1] if result else []
        return [
            StreamMessage(
                stream=self._stream,
                message_id=msg_id,
                data=msg_data,
            )
            for msg_id, msg_data in raw_messages
        ]

    async def listen(self) -> AsyncIterator[StreamMessage]:
        """Async generator that continuously yields new messages.

        Blocks until messages are available, then yields them one by one.
        Does NOT auto-ack -- caller must ack after processing.
        """
        while True:
            messages = await self.read()
            for msg in messages:
                yield msg

    def _parse_results(
        self, results: list[Any] | None
    ) -> list[StreamMessage]:
        """Parse raw xreadgroup results into StreamMessage objects."""
        if not results:
            return []
        messages: list[StreamMessage] = []
        for _stream_name, stream_messages in results:
            for msg_id, msg_data in stream_messages:
                messages.append(
                    StreamMessage(
                        stream=self._stream,
                        message_id=msg_id,
                        data=msg_data,
                    )
                )
        return messages
