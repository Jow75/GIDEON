import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any
from config.settings import settings
from providers.nvidia import NvidiaProvider
import os
import uuid
from memory.base import LongTermMemoryStore

class ChromaMemory(LongTermMemoryStore):
    """Manages persistent embeddings and semantic retrieval using ChromaDB."""

    def __init__(self):
        db_path = os.path.join(settings.data_dir, "chroma_db")
        os.makedirs(db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=db_path, settings=ChromaSettings(anonymized_telemetry=False))

        # For Phase 1 we will just inject NvidiaProvider globally but ideally pull from router
        self.provider = NvidiaProvider()
        self.embed_model = "nvidia/llama-nemotron-embed-1b-v2" # fallback default

        self.collection = self.client.get_or_create_collection(
            name="gideon_experiences",
            metadata={"hnsw:space": "cosine"}
        )

    async def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        return await self.provider.generate_embeddings(texts, model=self.embed_model)

    async def store_experience(self, text: str, metadata: Dict[str, Any] = None):
        """Stores a new experience in long-term memory."""
        embedding = (await self._get_embeddings([text]))[0]
        doc_id = str(uuid.uuid4())

        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata or {}]
        )
        return doc_id

    async def retrieve_relevant_experiences(self, query: str, n_results: int = 3, filter_metadata: Dict[str, Any] = None) -> List[str]:
        """Retrieves experiences semantically similar to the query, optionally filtering by metadata."""
        if self.collection.count() == 0:
            return []

        query_embedding = (await self._get_embeddings([query]))[0]
        query_kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": min(n_results, self.collection.count())
        }
        if filter_metadata:
            query_kwargs["where"] = filter_metadata

        results = self.collection.query(**query_kwargs)

        # ChromaDB returns a list of lists for documents
        if results and results["documents"] and len(results["documents"]) > 0:
            return results["documents"][0]
        return []
