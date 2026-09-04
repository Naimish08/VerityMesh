"""
Web Researcher Agent Node.

Searches the web for relevant sources, fetches content, chunks it,
generates embeddings, and stores everything in PostgreSQL.
"""

import logging
import uuid
from typing import Any

from agents.state import ResearchState
from agents.tools.web_search import TavilySearchTool
from agents.tools.content_fetcher import ContentFetcher
from services.chunking import chunk_text
from services.embeddings import EmbeddingService
from database.connection import AsyncSessionLocal
from database.models import Source, DocumentChunk

logger = logging.getLogger("veritymesh.web_researcher")


async def web_researcher_node(state: ResearchState) -> dict:
    """
    Web researcher node: for each sub-question, search the web,
    fetch source content, chunk it, embed it, and store in the database.
    """
    search_tool = TavilySearchTool()
    fetcher = ContentFetcher()
    embedder = EmbeddingService()
    research_id = state["research_id"]
    sub_questions = state.get("sub_questions", [state["question"]])
    max_results_per_question = state.get("config", {}).get("max_sources", 10) // max(len(sub_questions), 1)
    max_results_per_question = max(max_results_per_question, 2)

    all_sources: list[dict[str, Any]] = []
    all_chunks: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    errors: list[str] = []

    for sq_idx, sub_question in enumerate(sub_questions):
        logger.info(f"Researching sub-question {sq_idx + 1}/{len(sub_questions)}: {sub_question[:80]}...")

        try:
            results = await search_tool.search(sub_question, max_results=max_results_per_question)
        except Exception as e:
            logger.warning(f"Search failed for '{sub_question[:50]}': {e}")
            errors.append(f"Search failed: {str(e)}")
            continue

        for result in results:
            url = result.get("url", "")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)

            title = result.get("title", "Unknown")
            logger.info(f"  Fetching: {title[:60]} ({url[:80]})")

            # Fetch full page content
            try:
                content = await fetcher.fetch(url)
                if not content or len(content.strip()) < 100:
                    logger.warning(f"  Skipping {url}: insufficient content")
                    continue
            except Exception as e:
                logger.warning(f"  Failed to fetch {url}: {e}")
                errors.append(f"Fetch failed for {url}: {str(e)}")
                continue

            # Create source record in DB
            source_id = uuid.uuid4()
            try:
                async with AsyncSessionLocal() as session:
                    source = Source(
                        id=source_id,
                        research_run_id=uuid.UUID(research_id),
                        url=url,
                        title=title,
                        author=result.get("author"),
                        source_type=_classify_source_type(url),
                        content=content[:50000],  # Cap at 50k chars
                    )
                    session.add(source)
                    await session.commit()
            except Exception as e:
                logger.warning(f"  Failed to save source {url}: {e}")
                errors.append(f"DB save failed: {str(e)}")
                continue

            all_sources.append({
                "id": str(source_id),
                "url": url,
                "title": title,
                "source_type": _classify_source_type(url),
            })

            # Chunk the content
            chunks = chunk_text(content)
            logger.info(f"  Chunked into {len(chunks)} pieces")

            # Embed and store chunks
            for chunk_data in chunks:
                try:
                    embedding = await embedder.get_embedding(chunk_data["content"])

                    async with AsyncSessionLocal() as session:
                        doc_chunk = DocumentChunk(
                            id=uuid.uuid4(),
                            source_id=source_id,
                            content=chunk_data["content"],
                            chunk_index=chunk_data["chunk_index"],
                            embedding=embedding,
                            metadata_json={
                                "source_url": url,
                                "title": title,
                                "sub_question": sub_question,
                            },
                        )
                        session.add(doc_chunk)
                        await session.commit()

                    all_chunks.append({
                        "source_id": str(source_id),
                        "content": chunk_data["content"][:200],
                        "chunk_index": chunk_data["chunk_index"],
                    })
                except Exception as e:
                    logger.warning(f"  Failed to embed/store chunk: {e}")
                    errors.append(f"Embedding failed: {str(e)}")

    logger.info(
        f"Web research complete: {len(all_sources)} sources, "
        f"{len(all_chunks)} chunks, {len(errors)} errors"
    )

    return {
        "sources": all_sources,
        "chunks": all_chunks,
        "errors": errors,
        "current_step": "synthesizing",
    }


def _classify_source_type(url: str) -> str:
    """Classify source type based on URL patterns."""
    url_lower = url.lower()
    if any(d in url_lower for d in [".gov", ".edu", ".ac."]):
        return "official_documentation"
    elif any(d in url_lower for d in ["arxiv.org", "scholar.", "doi.org", "ieee.org", "acm.org"]):
        return "research_paper"
    elif any(d in url_lower for d in ["benchmark", "performance", "comparison"]):
        return "benchmark"
    elif any(d in url_lower for d in ["blog", "medium.com", "dev.to", "hashnode"]):
        return "technical_blog"
    elif any(d in url_lower for d in ["docs.", "documentation", "readme"]):
        return "official_documentation"
    elif any(d in url_lower for d in ["github.com", "gitlab.com"]):
        return "repository"
    else:
        return "web"
