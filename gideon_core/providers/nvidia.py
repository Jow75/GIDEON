import requests
from typing import List
from .base import AIProvider, Message
from config.settings import settings

class NvidiaProvider(AIProvider):
    """NVIDIA NIM provider implementation."""

    def __init__(self):
        self.api_key = settings.nvidia_api_key
        self.base_url = "https://integrate.api.nvidia.com/v1"
        if not self.api_key:
            raise ValueError("NVIDIA API key not configured.")

    def generate_completion(
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

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]
