"""Clientes opcionais para integração com modelos de linguagem."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


class LLMError(RuntimeError):
    """Erro de comunicação com provedor LLM."""


class LocalFallbackLLMClient:
    """Cliente local usado quando nenhum modelo LLM respondeu."""

    provider = "local-fallback"
    available = False

    def complete(self, *_: Any, **__: Any) -> str:
        raise LLMError("Nenhum provedor LLM disponível.")


class OllamaChatClient:
    """Cliente HTTP para modelo aberto local servido pelo Ollama."""

    available = True

    def __init__(self) -> None:
        self.model = os.getenv("AGENTEMED_OLLAMA_MODEL", "llama3.2:3b")
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.provider = f"ollama/{self.model}"

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history or [])
        messages.append({"role": "user", "content": user_prompt})
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 900,
            },
        }
        response = _post_json(
            f"{self.base_url.rstrip('/')}/api/chat",
            payload,
            {"Content-Type": "application/json"},
        )
        content = response.get("message", {}).get("content", "").strip()
        if not content:
            raise LLMError("Ollama não retornou conteúdo.")
        return content


class OpenAIChatClient:
    """Cliente HTTP mínimo para API compatível com chat completions."""

    provider = "openai"
    available = True

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "")
        if not self.api_key or not self.model:
            raise LLMError("Configure OPENAI_API_KEY e OPENAI_MODEL.")

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history or [])
        messages.append({"role": "user", "content": user_prompt})
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 900,
        }
        response = _post_json(
            "https://api.openai.com/v1/chat/completions",
            payload,
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        return response["choices"][0]["message"]["content"]


class AnthropicMessagesClient:
    """Cliente HTTP mínimo para API de mensagens da Anthropic."""

    provider = "anthropic"
    available = True

    def __init__(self) -> None:
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.model = os.getenv("ANTHROPIC_MODEL", "")
        if not self.api_key or not self.model:
            raise LLMError("Configure ANTHROPIC_API_KEY e ANTHROPIC_MODEL.")

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        payload = {
            "model": self.model,
            "max_tokens": 900,
            "temperature": 0.2,
            "system": system_prompt,
            "messages": [*(history or []), {"role": "user", "content": user_prompt}],
        }
        response = _post_json(
            "https://api.anthropic.com/v1/messages",
            payload,
            {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
        )
        return "\n".join(
            block.get("text", "")
            for block in response.get("content", [])
            if block.get("type") == "text"
        ).strip()


def make_llm_client(
    provider: str | None = None,
) -> LocalFallbackLLMClient | OllamaChatClient | OpenAIChatClient | AnthropicMessagesClient:
    """Cria cliente LLM conforme ambiente; cai para modo local se ausente."""
    selected = (provider or os.getenv("AGENTEMED_LLM_PROVIDER", "ollama")).lower()
    try:
        if selected == "ollama":
            return OllamaChatClient()
        if selected == "openai":
            return OpenAIChatClient()
        if selected == "anthropic":
            return AnthropicMessagesClient()
    except LLMError:
        return LocalFallbackLLMClient()
    return LocalFallbackLLMClient()


def _post_json(url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise LLMError(f"Falha na chamada ao LLM: {exc}") from exc
    return json.loads(raw)
