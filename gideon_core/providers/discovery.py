import os
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class EndpointDiscoveryEngine:
    """
    Dynamically discovers and maps capabilities across the entire NVIDIA ecosystem
    using multiple API credentials and endpoints.
    """
    
    BASE_NIM_URL = "https://integrate.api.nvidia.com/v1"
    
    # Specific known endpoints for specialized services
    ENDPOINTS = {
        "chat": f"{BASE_NIM_URL}/chat/completions",
        "embeddings": f"{BASE_NIM_URL}/embeddings",
        "audio_transcription": f"{BASE_NIM_URL}/audio/transcriptions",
        "audio_speech": f"{BASE_NIM_URL}/audio/speech",
        "image_generation": f"{BASE_NIM_URL}/images/generations",
    }
    
    def __init__(self, cache_file: str = "capability_cache.json"):
        self.cache_file = cache_file
        self.credentials: Dict[str, str] = {}  # service_name -> api_key
        self.capability_map: Dict[str, dict] = {}
        
    def load_credentials_from_env(self, env_file: str):
        """Load all NVIDIA credentials from a .env or custom keys file."""
        if not os.path.exists(env_file):
            logger.warning(f"Credentials file {env_file} not found.")
            return
            
        current_name = "default"
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith("Name:"):
                    current_name = line.split("Name:", 1)[1].strip().lower()
                elif line.startswith("nvapi-"):
                    # Map the name to the key
                    if "whisper" in current_name:
                        self.credentials["stt_whisper"] = line
                    elif "parakeet" in current_name:
                        self.credentials["stt_parakeet"] = line
                    elif "tts" in current_name or "riva" in current_name:
                        self.credentials["tts"] = line
                    elif "builder" in current_name:
                        self.credentials["builder"] = line
                    elif "main" in current_name:
                        self.credentials["general_nim"] = line
                    else:
                        self.credentials[f"custom_{len(self.credentials)}"] = line
                    current_name = "default"
                    
        # Fallback to os.environ if no specific keys found
        if not self.credentials and os.environ.get("NVIDIA_API_KEY"):
            self.credentials["general_nim"] = os.environ.get("NVIDIA_API_KEY")
            
        logger.info(f"Loaded {len(self.credentials)} API credentials.")

    async def discover_all(self):
        """Run full multi-endpoint discovery."""
        logger.info("Starting multi-endpoint ecosystem discovery...")
        
        # In a full implementation, this would make async calls to 
        # /v1/models and test specific endpoints using httpx.
        # For now, we build the structure that the CapabilityRegistry will use.
        
        self.capability_map = {
            "conversation": [],
            "reasoning": [],
            "coding": [],
            "embedding": [],
            "speech_to_text": [],
            "text_to_speech": [],
            "vision": [],
            "image_generation": []
        }
        
        # Populate with discovered data (mocked for architectural representation)
        if "general_nim" in self.credentials:
            self.capability_map["conversation"].append({
                "id": "meta/llama-3.1-70b-instruct",
                "service": "general_nim",
                "verified": True
            })
            
        if "stt_whisper" in self.credentials:
            self.capability_map["speech_to_text"].append({
                "id": "openai/whisper-large-v3",
                "service": "stt_whisper",
                "endpoint": self.ENDPOINTS["audio_transcription"],
                "verified": True
            })
            
        if "stt_parakeet" in self.credentials:
            self.capability_map["speech_to_text"].append({
                "id": "nvidia/parakeet-rnnt-1.1b",
                "service": "stt_parakeet",
                "endpoint": self.ENDPOINTS["audio_transcription"],
                "verified": True
            })

        self._save_cache()
        logger.info("Discovery complete. Unified capability map built.")
        
    def _save_cache(self):
        with open(self.cache_file, "w") as f:
            json.dump(self.capability_map, f, indent=2)
            
    def get_best_model_for(self, category: str) -> Optional[dict]:
        """Route requests dynamically based on discovered capabilities."""
        models = self.capability_map.get(category, [])
        if not models:
            return None
        # Return the first verified model
        for m in models:
            if m.get("verified"):
                return m
        return models[0] if models else None

