import uuid
from typing import List, Dict, Any
import qdrant_client
from qdrant_client.models import Distance, VectorParams, PointStruct
from config.settings import settings
from providers.nvidia import NvidiaProvider
from memory.base import LongTermMemoryStore
import os

class QdrantMemory(LongTermMemoryStore):
    """Manages persistent embeddings and semantic retrieval using Qdrant."""

    def __init__(self):
        url = getattr(settings, "qdrant_url", "http://localhost:6333")
        self.client = qdrant_client.QdrantClient(url=url)
        self.collection_name = "gideon_experiences"
        
        # For Phase 1 we will just inject NvidiaProvider globally but ideally pull from router
        self.provider = NvidiaProvider()
        self.embed_model = "nvidia/llama-nemotron-embed-1b-v2" # fallback default
        
        # Ensure collection exists (assume embedding size of 1024 for standard local/nvidia models, adjust if needed)
        # Note: nvidia/llama-nemotron-embed-1b-v2 produces 1024-d embeddings
        self._ensure_collection(1024)

    def _ensure_collection(self, vector_size: int):
        if not self.client.collection_exists(collection_name=self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    async def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        return await self.provider.generate_embeddings(texts, model=self.embed_model)

    async def store_experience(self, text: str, metadata: Dict[str, Any] = None) -> str:
        """Stores a new experience in long-term memory."""
        embedding = (await self._get_embeddings([text]))[0]
        doc_id = str(uuid.uuid4())

        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=doc_id,
                    vector=embedding,
                    payload={"text": text, **(metadata or {})}
                )
            ]
        )
        return doc_id

    async def retrieve_relevant_experiences(self, query: str, n_results: int = 3, filter_metadata: Dict[str, Any] = None) -> List[str]:
        """Retrieves experiences semantically similar to the query, optionally filtering by metadata."""
        query_embedding = (await self._get_embeddings([query]))[0]
        
        # Qdrant client provides search
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=n_results
            # filter=... # implement Qdrant filter structure if needed
        )
        
        results = []
        for hit in search_result:
            if "text" in hit.payload:
                results.append(hit.payload["text"])
        
        
        return results

    async def stop(self):
        """Releases Qdrant client resources."""
        if hasattr(self, 'client') and self.client:
            self.client.close()
