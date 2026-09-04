"""
API routes for research operations.
"""

import json
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.research import (
    ResearchRequest,
    ResearchResponse,
    ResearchDetailResponse,
    ClaimResponse,
    SourceResponse,
)
from database.connection import get_db
from database.models import ResearchRun, ResearchStatus, ResearchDepth, Source, Claim
from core.redis import redis_client

logger = logging.getLogger("veritymesh.routes")

router = APIRouter(prefix="/api/research", tags=["research"])


@router.post("", response_model=ResearchResponse, status_code=201)
async def create_research(req: ResearchRequest, db: AsyncSession = Depends(get_db)):
    """Start a new research run."""
    run = ResearchRun(
        id=uuid.uuid4(),
        question=req.question,
        status=ResearchStatus.PENDING,
        depth=ResearchDepth(req.depth),
        config=req.model_dump(),
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    # Enqueue for the worker
    await redis_client.enqueue_research(str(run.id), req.model_dump())

    # If running in local in-memory mode, launch worker task in background
    if redis_client.is_in_memory:
        import asyncio
        from agents.graph import run_research
        asyncio.create_task(run_research(
            research_id=str(run.id),
            question=run.question,
            config=req.model_dump(),
            redis_client=redis_client,
        ))

    logger.info(f"Created research run {run.id} for: {req.question[:80]}...")
    return run


@router.get("/{research_id}", response_model=ResearchDetailResponse)
async def get_research(research_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get full details of a research run."""
    stmt = select(ResearchRun).where(ResearchRun.id == research_id)
    result = await db.execute(stmt)
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found")
    return run


@router.get("/{research_id}/events")
async def get_research_events(research_id: str):
    """SSE stream of real-time research progress events."""

    async def event_generator():
        try:
            async for event in redis_client.subscribe_events(research_id):
                event_type = event.get("event_type", "message")
                data = json.dumps(event)
                yield f"event: {event_type}\ndata: {data}\n\n"

                # Stop streaming when research is complete or failed
                if event_type in ("complete", "error"):
                    if not event.get("data", {}).get("recoverable", False):
                        break
        except Exception as e:
            logger.error(f"SSE stream error: {e}")
            yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{research_id}/claims", response_model=list[ClaimResponse])
async def get_research_claims(
    research_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    """Get all claims extracted for a research run."""
    stmt = select(Claim).where(Claim.research_run_id == research_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{research_id}/sources", response_model=list[SourceResponse])
async def get_research_sources(
    research_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    """Get all sources discovered for a research run."""
    stmt = select(Source).where(Source.research_run_id == research_id)
    result = await db.execute(stmt)
    return result.scalars().all()
