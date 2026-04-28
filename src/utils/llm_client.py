"""
LLM API Client
Supports multiple LLM providers: OpenAI, Claude, MiniMax, etc.
"""

import os
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """LLM response container"""
    content: str
    raw: Dict
    model: str
    usage: Dict[str, int]
    finish_reason: str


class LLMClient:
    """
    Unified LLM API client supporting multiple providers.
    
    Supported providers:
    - OpenAI (GPT-3.5, GPT-4)
    - MiniMax (abab6-chat)
    - Anthropic (Claude)
    - Custom endpoints
    """
    
    PROVIDERS = {
        "openai": "https://api.openai.com/v1",
        "minimax": "https://api.minimax.chat/v1",
        "anthropic": "https://api.anthropic.com/v1",
    }
    
    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        timeout: int = 60
    ):
        """
        Initialize LLM client.
        
        Args:
            provider: Provider name (openai, minimax, anthropic)
            api_key: API key for authentication
            base_url: Custom API base URL
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
        """
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY", "")
        self.base_url = base_url or self.PROVIDERS.get(self.provider, "")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        
        self._client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize HTTP client"""
        import httpx
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=self.timeout
        )
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Send chat completion request.
        
        Args:
            messages: List of message dicts with role and content
            stream: Enable streaming response
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            
        Returns:
            Generated text response
        """
        if self.provider == "openai" or not self.provider:
            return self._chat_openai(
                messages, stream, temperature, max_tokens, **kwargs
            )
        elif self.provider == "minimax":
            return self._chat_minimax(
                messages, stream, temperature, max_tokens, **kwargs
            )
        elif self.provider == "anthropic":
            return self._chat_anthropic(
                messages, stream, temperature, max_tokens, **kwargs
            )
        else:
            return self._chat_openai(
                messages, stream, temperature, max_tokens, **kwargs
            )
    
    def _chat_openai(
        self,
        messages: List[Dict],
        stream: bool,
        temperature: Optional[float],
        max_tokens: Optional[int],
        **kwargs
    ) -> str:
        """OpenAI-compatible chat completion"""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
            **kwargs
        }
        
        # Filter None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        response = self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        if stream:
            # Return empty for streaming (implement async generator if needed)
            return ""
        
        return result["choices"][0]["message"]["content"]
    
    def _chat_minimax(
        self,
        messages: List[Dict],
        stream: bool,
        temperature: Optional[float],
        max_tokens: Optional[int],
        **kwargs
    ) -> str:
        """MiniMax chat completion"""
        # Convert messages format for MiniMax
        minimax_messages = []
        for msg in messages:
            if msg["role"] == "system":
                minimax_messages.append({"role": "system", "content": msg["content"]})
            elif msg["role"] == "user":
                minimax_messages.append({"role": "USER", "content": msg["content"]})
            elif msg["role"] == "assistant":
                minimax_messages.append({"role": "BOT", "content": msg["content"]})
        
        payload = {
            "model": self.model,
            "messages": minimax_messages,
            "stream": stream,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
            **kwargs
        }
        
        # Update headers for MiniMax
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        response = self._client.post(
            "/text/chatcompletion_v2",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["messages"][-1]["text"]
    
    def _chat_anthropic(
        self,
        messages: List[Dict],
        stream: bool,
        temperature: Optional[float],
        max_tokens: Optional[int],
        **kwargs
    ) -> str:
        """Anthropic Claude chat completion"""
        # Extract system message
        system_msg = ""
        anthropic_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg += msg["content"] + "\n"
            else:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        payload = {
            "model": self.model,
            "messages": anthropic_messages,
            "stream": stream,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }
        
        if system_msg:
            payload["system"] = system_msg
        
        # Update headers for Anthropic
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        response = self._client.post(
            "/messages",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        
        result = response.json()
        return result["content"][0]["text"]
    
    def chat_with_functions(
        self,
        messages: List[Dict],
        functions: List[Dict],
        function_call: Optional[str] = None
    ) -> Dict:
        """
        Chat with function calling (OpenAI format).
        
        Args:
            messages: Chat messages
            functions: Function definitions
            function_call: Force specific function
            
        Returns:
            Response with optional function_call
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": functions,
        }
        
        if function_call:
            payload["tool_choice"] = {"type": "function", "function": {"name": function_call}}
        
        response = self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        
        result = response.json()
        message = result["choices"][0]["message"]
        
        # Parse tool calls if present
        if "tool_calls" in message:
            return {
                "content": message.get("content", ""),
                "function_call": {
                    "name": message["tool_calls"][0]["function"]["name"],
                    "arguments": message["tool_calls"][0]["function"]["arguments"]
                }
            }
        
        return {"content": message["content"]}
    
    def embed(
        self,
        texts: Union[str, List[str]],
        model: Optional[str] = None
    ) -> List[List[float]]:
        """
        Get text embeddings.
        
        Args:
            texts: Text or list of texts
            model: Embedding model
            
        Returns:
            List of embedding vectors
        """
        if isinstance(texts, str):
            texts = [texts]
        
        payload = {
            "model": model or "text-embedding-ada-002",
            "input": texts
        }
        
        response = self._client.post("/embeddings", json=payload)
        response.raise_for_status()
        
        result = response.json()
        return [item["embedding"] for item in result["data"]]
    
    def close(self):
        """Close the HTTP client"""
        if self._client:
            self._client.close()
