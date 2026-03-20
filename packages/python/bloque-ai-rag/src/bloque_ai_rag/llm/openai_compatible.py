"""OpenAI-compatible LLM client for DeepSeek, OpenAI, and similar APIs."""

from __future__ import annotations

import httpx

from bloque_ai_rag.models.settings import LLMSettings


class OpenAICompatibleClient:
    """Client for any OpenAI-compatible chat completions API.

    Covers DeepSeek, OpenAI, and any provider that implements
    the /v1/chat/completions endpoint.

    Example:
        settings = LLMSettings(provider="deepseek", api_key="sk-...")
        client = OpenAICompatibleClient(settings)
        await client.start()
        answer = await client.generate("What is Python?", context="Python is a language.")
        await client.stop()
    """

    def __init__(
        self,
        settings: LLMSettings | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings or LLMSettings()
        self._external_client = http_client is not None
        self._client = http_client

    async def start(self) -> None:
        """Create the httpx.AsyncClient if not provided externally."""
        if self._client is not None:
            return
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.settings.timeout, connect=10.0),
        )

    async def stop(self) -> None:
        """Close the httpx.AsyncClient if we own it."""
        if self._client is not None and not self._external_client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the httpx client. Raises RuntimeError if not started."""
        if self._client is None:
            raise RuntimeError(
                "OpenAICompatibleClient is not started. Call start() or use async with."
            )
        return self._client

    async def generate(self, prompt: str, context: str = "") -> str:
        """Generate a response using the chat completions API.

        Args:
            prompt: User message text.
            context: Optional context to inject into the system prompt.

        Returns:
            Generated text response.
        """
        base_url = self.settings.get_base_url()
        model = self.settings.get_model()
        url = f"{base_url}/v1/chat/completions"

        messages: list[dict[str, str]] = []

        if context:
            system_content = self.settings.system_prompt.format(context=context)
            messages.append({"role": "system", "content": system_content})

        messages.append({"role": "user", "content": prompt})

        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.settings.api_key:
            headers["Authorization"] = f"Bearer {self.settings.api_key}"

        payload = {
            "model": model,
            "messages": messages,
            "temperature": self.settings.temperature,
            "max_tokens": self.settings.max_tokens,
        }

        response = await self.client.post(url, json=payload, headers=headers)
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def health_check(self) -> bool:
        """Check if the LLM API is reachable via models endpoint."""
        try:
            base_url = self.settings.get_base_url()
            url = f"{base_url}/v1/models"
            headers: dict[str, str] = {}
            if self.settings.api_key:
                headers["Authorization"] = f"Bearer {self.settings.api_key}"
            response = await self.client.get(url, headers=headers, timeout=5.0)
            return response.status_code < 500
        except Exception:
            return False

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()
