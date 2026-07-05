from providers.base import AIProvider, Message
from providers.nvidia import NvidiaProvider
from providers.registry import CapabilityRegistry
from typing import List

class AIOperationsRouter:
    """Routes tasks to the appropriate model/provider based on required capabilities."""
    def __init__(self):
        self.registry = CapabilityRegistry()
        self.providers = {
            "nvidia": NvidiaProvider()
            # Future providers can be registered here
        }

    def execute_task(self, required_tags: List[str], messages: List[Message]) -> str:
        capability = self.registry.find_model(required_tags)
        if not capability:
            raise ValueError(f"No model found for capabilities: {required_tags}")

        provider = self.providers.get(capability.provider_name)
        if not provider:
            raise ValueError(f"Provider {capability.provider_name} not configured.")

        return provider.generate_completion(messages=messages, model=capability.model_id)
