from providers.base import Message
from providers.nvidia import NvidiaProvider
from providers.discovery import EndpointDiscoveryEngine
from config.settings import settings
from typing import List

class AIOperationsRouter:
    """Routes tasks dynamically using Endpoint Discovery."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.discovery = EndpointDiscoveryEngine()
        self.discovery.load_credentials_from_env(settings.credentials_file)
        # We must call discover_all() before routing, usually in an async startup
        self._initialized = True

    async def initialize(self):
        if not self.discovery.capability_map:
            await self.discovery.discover_all()

    async def execute_task(self, required_tags: List[str], messages: List[Message]) -> str:
        await self.initialize()
        
        # Determine category based on tags (simplified mapping)
        category = "conversation"
        if "reasoning" in required_tags: category = "reasoning"
        if "coding" in required_tags: category = "coding"
        
        model_info = self.discovery.get_best_model_for(category)
        if not model_info:
            raise ValueError(f"No discovered model for category: {category}")

        service = model_info.get("service")
        model_id = model_info.get("id")
        endpoint = model_info.get("endpoint", "https://integrate.api.nvidia.com/v1")
        api_key = self.discovery.credentials.get(service)

        provider = NvidiaProvider(api_key=api_key, base_url=endpoint.replace("/chat/completions", ""))
        
        return await provider.generate_completion(messages=messages, model=model_id)

