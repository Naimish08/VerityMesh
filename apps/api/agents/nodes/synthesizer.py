"""
Synthesizer Agent Node.

Takes all collected sources and chunks, retrieves the most relevant evidence,
and generates an evidence-backed report with source citations.
"""

import logging
import uuid

from langchain_google_genai import ChatGoogleGenerativeAI

from agents.state import ResearchState
from agents.prompts.synthesizer import SYNTHESIZER_SYSTEM_PROMPT
from services.retrieval import RetrievalService
from services.embeddings import EmbeddingService
from database.connection import AsyncSessionLocal
from database.models import Claim, Citation
from config import settings

logger = logging.getLogger("veritymesh.synthesizer")


async def synthesizer_node(state: ResearchState) -> dict:
    """
    Synthesizer node: retrieves relevant evidence for each sub-question
    and generates a comprehensive, cited report.
    """
    question = state["question"]
    sub_questions = state.get("sub_questions", [question])
    sources = state.get("sources", [])
    research_id = state["research_id"]

    logger.info(f"Synthesizing report from {len(sources)} sources...")

    # Build context by retrieving relevant chunks for each sub-question
    context_sections: list[str] = []
    source_map: dict[str, dict] = {}  # source_id -> source info

    # Map sources for quick lookup
    for src in sources:
        source_map[src["id"]] = src

    async with AsyncSessionLocal() as session:
        retrieval = RetrievalService(session)

        for sq_idx, sub_q in enumerate(sub_questions):
            try:
                relevant_chunks = await retrieval.semantic_search(sub_q, limit=5)
                if relevant_chunks:
                    section = f"\n--- Evidence for: {sub_q} ---\n"
                    for chunk in relevant_chunks:
                        src_id = str(chunk.source_id)
                        src_info = source_map.get(src_id, {})
                        section += (
                            f"\n[Source: {src_info.get('title', 'Unknown')} | "
                            f"URL: {src_info.get('url', 'N/A')} | "
                            f"ID: {src_id[:8]}]\n"
                            f"{chunk.content}\n"
                        )
                    context_sections.append(section)
            except Exception as e:
                logger.warning(f"Retrieval failed for sub-question {sq_idx}: {e}")
                context_sections.append(f"\n--- No evidence retrieved for: {sub_q} ---\n")

    # Build the full context
    full_context = "\n".join(context_sections)
    if not full_context.strip():
        # Fallback: use raw chunk content from state
        for chunk in state.get("chunks", [])[:15]:
            full_context += f"\n{chunk.get('content', '')}\n"

    # Build source reference list
    source_ref = "\n".join(
        f"[Source {i+1}] {s.get('title', 'Unknown')} — {s.get('url', 'N/A')}"
        for i, s in enumerate(sources)
    )

    # Generate the report
    llm = ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.2,
        max_output_tokens=4096,
    )

    messages = [
        ("system", SYNTHESIZER_SYSTEM_PROMPT),
        ("human", (
            f"RESEARCH QUESTION:\n{question}\n\n"
            f"SUB-QUESTIONS:\n" + "\n".join(f"- {sq}" for sq in sub_questions) + "\n\n"
            f"AVAILABLE SOURCES:\n{source_ref}\n\n"
            f"EVIDENCE:\n{full_context}"
        )),
    ]

    try:
        response = await llm.ainvoke(messages)
        if isinstance(response.content, str):
            report = response.content
        elif isinstance(response.content, list):
            parts = []
            for item in response.content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict) and "text" in item:
                    parts.append(item["text"])
            report = "".join(parts)
        else:
            report = str(response.content)
        logger.info(f"Report generated: {len(report)} characters")
    except Exception as e:
        logger.error(f"Synthesis failed: {e}", exc_info=True)
        report = (
            f"# Research Report\n\n"
            f"## Error\n"
            f"The synthesis agent encountered an error: {str(e)}\n\n"
            f"## Collected Sources\n"
            + "\n".join(f"- [{s.get('title', 'Unknown')}]({s.get('url', '')})" for s in sources)
        )

    # Extract basic claims from the report and store them
    claims_data: list[dict] = []
    try:
        async with AsyncSessionLocal() as session:
            # Store the report result
            from sqlalchemy import update
            from database.models import ResearchRun
            stmt = update(ResearchRun).where(
                ResearchRun.id == uuid.UUID(research_id)
            ).values(result={
                "report": report,
                "sources_count": len(sources),
                "sub_questions": sub_questions,
            })
            await session.execute(stmt)
            await session.commit()
    except Exception as e:
        logger.warning(f"Failed to save report to DB: {e}")

    return {
        "report": report,
        "citations": [
            {"source_id": s["id"], "title": s.get("title", ""), "url": s.get("url", "")}
            for s in sources
        ],
        "current_step": "completed",
    }
