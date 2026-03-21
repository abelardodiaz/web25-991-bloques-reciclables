"""Protocol for LLM provider implementations."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol that all LLM clients must satisfy.

    Duck-typed: any object with generate and health_check
    can be used as an LLM provider without inheriting this class.
    """

    async def generate(self, prompt: str, context: str = "") -> str: ...

    async def health_check(self) -> bool: ...
