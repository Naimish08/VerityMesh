"""
Embedding service using Google's text-embedding-004 model.
Includes Redis cache-aside for performance.
"""

import hashlib
import logging
from typing import Any

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config import settings
from core.redis import redis_client

logger = logging.getLogger("veritymesh.embeddings")


def _fallback_embedding(text: str, dimensions: int = 768) -> list[float]:
    """Deterministic unit-normalized vector for graceful fallback if embedding API fails."""
    import math, random
    rng = random.Random(hashlib.sha256(text.encode("utf-8")).digest())
    vec = [rng.gauss(0, 1) for _ in range(dimensions)]
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


class EmbeddingService:
    """Service for generating and caching text embeddings."""

    def __init__(self):
        try:
            self._model = GoogleGenerativeAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                output_dimensionality=settings.EMBEDDING_DIMENSIONS,
            )
        except Exception as e:
            logger.warning(f"Could not initialize GoogleGenerativeAIEmbeddings: {e}")
            self._model = None

    async def get_embedding(self, text: str) -> list[float]:
        """Get embedding for a single text, with cache-aside."""
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        cache_key = f"embed:{text_hash}"

        # Try cache first
        if redis_client.is_connected:
            try:
                cached = await redis_client.cache_get(cache_key)
                if cached is not None and len(cached) == settings.EMBEDDING_DIMENSIONS:
                    return cached
            except Exception as e:
                logger.warning(f"Cache read failed: {e}")

        # Generate embedding
        result = None
        if self._model:
            try:
                result = await self._model.aembed_query(text)
            except Exception as e:
                logger.warning(f"Google embedding generation failed ({e}), using fallback vector")
                result = None

        if not result or len(result) != settings.EMBEDDING_DIMENSIONS:
            result = _fallback_embedding(text, dimensions=settings.EMBEDDING_DIMENSIONS)

        # Cache the result (7-day TTL)
        if redis_client.is_connected:
            try:
                await redis_client.cache_set(cache_key, result, ttl=604800)
            except Exception as e:
                logger.warning(f"Cache write failed: {e}")

        return result

    async def get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Get embeddings for multiple texts. Uses batch API where possible."""
        # For small batches, use individual calls with caching
        if len(texts) <= 3:
            return [await self.get_embedding(t) for t in texts]

        # For larger batches, use the batch API directly
        try:
            results = await self._model.aembed_documents(texts)
            return results
        except Exception as e:
            logger.error(f"Batch embedding failed, falling back to individual: {e}")
            return [await self.get_embedding(t) for t in texts]
