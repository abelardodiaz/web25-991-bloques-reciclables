"""Redis Streams producer."""

from __future__ import annotations

from typing import Any

from ulfblk_core.logging import get_logger

from ..client.manager import RedisManager

logger = get_logger(__name__)


class StreamProducer:
    """Publishes messages to a Redis Stream.

    Args:
        manager: Connected RedisManager.
        stream: Default stream name.
        maxlen: Optional max stream length (approximate trimming).
    """

    def __init__(
        self,
        manager: RedisManager,
        stream: str,
        maxlen: int | None = None,
    ) -> None:
        self._manager = manager
        self._stream = stream
        self._maxlen = maxlen

    async def publish(
        self,
        data: dict[str, Any],
        stream: str | None = None,
        message_id: str = "*",
        tenant_id: str | None = None,
    ) -> str:
        """Publish a message to the stream.

        Args:
            data: Message payload (values are coerced to str by Redis).
            stream: Override the default stream name.
            message_id: Message ID, "*" for auto-generated.
            tenant_id: Optional tenant for key prefixing.

        Returns:
            The message ID assigned by Redis.
        """
        target = stream or self._stream
        full_key = self._manager.make_key(target, tenant_id=tenant_id)
        result = await self._manager.client.xadd(
            full_key,
            data,
            id=message_id,
            maxlen=self._maxlen,
            approximate=self._maxlen is not None,
        )
        logger.debug("stream_published", stream=full_key, message_id=result)
        return result

    async def stream_length(
        self,
        stream: str | None = None,
        tenant_id: str | None = None,
    ) -> int:
        """Get the number of messages in the stream."""
        target = stream or self._stream
        full_key = self._manager.make_key(target, tenant_id=tenant_id)
        return await self._manager.client.xlen(full_key)
