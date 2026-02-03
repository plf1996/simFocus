from typing import Optional, Dict, Any, AsyncGenerator
import httpx
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        pass

    @abstractmethod
    async def generate_stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Generate text from prompt with streaming"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        model: str = "gpt-4"
    ):
        self.api_key = api_key
        self.base_url = base_url or "https://api.openai.com/v1"
        self.model = model
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )

    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text from OpenAI API"""
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens or 500,
        }

        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()

        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})

        return {
            "content": content,
            "tokens": usage.get("total_tokens", 0)
        }

    async def generate_stream(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate text from OpenAI API with streaming"""
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens or 500,
            "stream": True
        }

        async with self.client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        import json
                        data = json.loads(data_str)
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield {
                                    "content": delta["content"],
                                    "is_complete": False
                                }
                            finish_reason = data["choices"][0].get("finish_reason")
                            if finish_reason:
                                yield {
                                    "content": "",
                                    "is_complete": True,
                                    "finish_reason": finish_reason
                                }
                    except json.JSONDecodeError:
                        pass

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider"""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022"
    ):
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(
            base_url="https://api.anthropic.com/v1",
            headers={
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            timeout=60.0
        )

    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text from Anthropic API"""
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens or 500,
        }

        response = await self.client.post("/messages", json=payload)
        response.raise_for_status()
        data = response.json()

        content = data["content"][0]["text"]
        usage = data.get("usage", {})

        return {
            "content": content,
            "tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
        }

    async def generate_stream(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate text from Anthropic API with streaming"""
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens or 500,
            "stream": True
        }

        async with self.client.stream("POST", "/messages", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    try:
                        import json
                        data = json.loads(data_str)
                        if data["type"] == "content_block_delta":
                            yield {
                                "content": data["delta"]["text"],
                                "is_complete": False
                            }
                        elif data["type"] == "message_stop":
                            yield {
                                "content": "",
                                "is_complete": True,
                                "finish_reason": "stop"
                            }
                    except json.JSONDecodeError:
                        pass

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class LLMOrchestrator:
    """Orchestrator for managing multiple LLM providers"""

    def __init__(self):
        self._providers: Dict[str, LLMProvider] = {}

    def register_provider(
        self,
        name: str,
        provider_type: str,
        api_key: str,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        """Register a new LLM provider"""
        if provider_type == "openai":
            self._providers[name] = OpenAIProvider(
                api_key=api_key,
                base_url=base_url,
                model=model or "gpt-4"
            )
        elif provider_type == "anthropic":
            self._providers[name] = AnthropicProvider(
                api_key=api_key,
                model=model or "claude-3-5-sonnet-20241022"
            )
        elif provider_type == "custom":
            # Custom provider uses OpenAI-compatible API
            # base_url must be provided for custom providers
            if not base_url:
                raise ValueError(f"base_url is required for custom providers")
            self._providers[name] = OpenAIProvider(
                api_key=api_key,
                base_url=base_url,
                model=model or "gpt-4"
            )
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")

    def get_provider(self, name: str) -> Optional[LLMProvider]:
        """Get a registered provider"""
        return self._providers.get(name)

    async def generate(
        self,
        provider_name: str,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using specified provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider not found: {provider_name}")

        return await provider.generate(prompt, **kwargs)

    async def generate_stream(
        self,
        provider_name: str,
        prompt: str,
        **kwargs
    ):
        """Generate text using specified provider with streaming"""
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider not found: {provider_name}")

        async for chunk in provider.generate_stream(prompt, **kwargs):
            yield chunk

    async def close_all(self):
        """Close all provider connections"""
        for provider in self._providers.values():
            await provider.close()
        self._providers.clear()
