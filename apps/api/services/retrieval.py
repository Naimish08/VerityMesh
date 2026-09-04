"""
Retrieval service for vector similarity search using pgvector.
"""

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import DocumentChunk
from services.embeddings import EmbeddingService

logger = logging.getLogger("veritymesh.retrieval")


class RetrievalService:
    """Service for semantic search over document chunks."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._embedder = EmbeddingService()

    async def semantic_search(
        self,
        query: str,
        limit: int = 5,
        source_ids: list[UUID] | None = None,
    ) -> list[DocumentChunk]:
        """
        Search for chunks semantically similar to the query.
        
        Optionally filter by specific source IDs to scope the search
        to a particular research run's sources.
        """
        query_embedding = await self._embedder.get_embedding(query)

        stmt = (
            select(DocumentChunk)
            .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )

        if source_ids:
            stmt = stmt.where(DocumentChunk.source_id.in_(source_ids))

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def hybrid_search(
        self,
        query: str,
        keyword_query: str | None = None,
        limit: int = 5,
    ) -> list[DocumentChunk]:
        """
        Hybrid search combining vector similarity and keyword matching.
        Falls back to pure semantic search for MVP.
        """
        # MVP: use semantic search only
        return await self.semantic_search(query, limit=limit)
