import httpx
from typing import List
from .base import AIProvider, Message
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class NvidiaProvider(AIProvider):
    """NVIDIA NIM provider implementation."""

    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or settings.nvidia_api_key
        self.base_url = base_url or "https://integrate.api.nvidia.com/v1"
        if not self.api_key:
            raise ValueError("NVIDIA API key not configured.")

    async def generate_completion(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        payload = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def generate_embeddings(self, texts: List[str], model: str) -> List[List[float]]:
        """Generate embeddings using the NVIDIA API."""
        url = f"{self.base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        payload = {
            "input": texts,
            "model": model,
            "input_type": "query"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()
            # Sort by index to ensure order matches input
            embeddings = [item["embedding"] for item in sorted(data["data"], key=lambda x: x["index"])]
            return embeddings
