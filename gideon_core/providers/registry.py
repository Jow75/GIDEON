from typing import Optional

class ModelCapability:
    def __init__(self, provider_name: str, model_id: str, tags: list[str], cost_tier: str = "low"):
        self.provider_name = provider_name
        self.model_id = model_id
        self.tags = tags
        self.cost_tier = cost_tier

class CapabilityRegistry:
    """Registry to dynamically map capabilities to specific models and providers."""
    def __init__(self):
        self.models: list[ModelCapability] = []
        self._initialize_defaults()

    def _initialize_defaults(self):
        # Register models based on our NVIDIA audit that we actually verified
        self.register(ModelCapability("nvidia", "meta/llama-3.1-70b-instruct", ["commander", "reasoning", "general"]))
        self.register(ModelCapability("nvidia", "meta/llama-3.1-8b-instruct", ["fast", "formatting", "background"]))

        # The specific coding models audited seem to throw 404s on the /chat/completions endpoint for this specific key tier.
        # We will fallback to the general reasoning model (llama-3.1-70b-instruct) for coding tasks for now to maintain stability.
        self.register(ModelCapability("nvidia", "meta/llama-3.1-70b-instruct", ["coding"]))

        self.register(ModelCapability("nvidia", "nvidia/nv-embed-v1", ["embedding"]))

    def register(self, capability: ModelCapability):
        self.models.append(capability)

    def find_model(self, required_tags: list[str]) -> Optional[ModelCapability]:
        """Find the first model that satisfies all required tags."""
        for model in self.models:
            if all(tag in model.tags for tag in required_tags):
                return model
        return None
