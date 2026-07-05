import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any
from config.settings import settings
from providers.nvidia import NvidiaProvider
from providers.registry import CapabilityRegistry
import os
import uuid

class LongTermMemory:
    """Manages persistent embeddings and semantic retrieval (Experience Memory)."""

    def __init__(self):
        db_path = os.path.join(settings.data_dir, "chroma_db")
        os.makedirs(db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=db_path, settings=ChromaSettings(anonymized_telemetry=False))

        # In a full implementation, we'd use the router. Here we inject the provider for embeddings.
        self.provider = NvidiaProvider()
        registry = CapabilityRegistry()
        self.embed_model = registry.find_model(["embedding"]).model_id

        self.collection = self.client.get_or_create_collection(
            name="gideon_experiences",
            metadata={"hnsw:space": "cosine"}
        )

    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self.provider.generate_embeddings(texts, model=self.embed_model)

    def store_experience(self, text: str, metadata: Dict[str, Any] = None):
        """Stores a new experience in long-term memory."""
        embedding = self._get_embeddings([text])[0]
        doc_id = str(uuid.uuid4())

        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata or {}]
        )
        return doc_id

    def retrieve_relevant_experiences(self, query: str, n_results: int = 3) -> List[str]:
        """Retrieves experiences semantically similar to the query."""
        if self.collection.count() == 0:
            return []

        query_embedding = self._get_embeddings([query])[0]
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, self.collection.count())
        )

        # ChromaDB returns a list of lists for documents
        if results and results["documents"] and len(results["documents"]) > 0:
            return results["documents"][0]
        return []
