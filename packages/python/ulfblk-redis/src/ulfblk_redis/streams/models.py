"""Stream message data model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StreamMessage:
    """A message read from a Redis Stream."""

    stream: str
    message_id: str
    data: dict[str, str]
