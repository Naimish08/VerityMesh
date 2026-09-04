"""
Research Worker — Background process that dequeues research jobs from Redis
and executes the LangGraph pipeline.
"""

import asyncio
import logging
import signal
import sys
import uuid

from sqlalchemy import select, update

from core.redis import redis_client
from database.connection import AsyncSessionLocal
from database.models import ResearchRun, ResearchStatus
from agents.graph import run_research

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("veritymesh.worker")

shutdown_event = asyncio.Event()


def handle_shutdown(sig, frame):
    """Handle graceful shutdown signals."""
    logger.info(f"Received signal {sig}, shutting down gracefully...")
    shutdown_event.set()


async def process_queue():
    """Main worker loop: dequeue jobs and run the research pipeline."""
    await redis_client.connect()
    logger.info("Worker started. Waiting for research jobs...")

    while not shutdown_event.is_set():
        try:
            task = await redis_client.dequeue_research()
            if task is None:
                await asyncio.sleep(0.5)
                continue

            research_id = task["research_id"]
            config = task.get("config", {})

            logger.info(f"Processing research job: {research_id}")

            # Fetch the research run from DB
            async with AsyncSessionLocal() as session:
                stmt = select(ResearchRun).where(
                    ResearchRun.id == uuid.UUID(research_id)
                )
                result = await session.execute(stmt)
                run = result.scalar_one_or_none()

                if not run:
                    logger.error(f"Research run {research_id} not found in database")
                    continue

                question = run.question

            # Run the research pipeline
            try:
                await run_research(
                    research_id=research_id,
                    question=question,
                    config=config,
                    redis_client=redis_client,
                )
                logger.info(f"Research job {research_id} completed successfully")

            except Exception as e:
                logger.error(f"Research job {research_id} failed: {e}", exc_info=True)

                # Mark as FAILED in the database
                async with AsyncSessionLocal() as session:
                    stmt = update(ResearchRun).where(
                        ResearchRun.id == uuid.UUID(research_id)
                    ).values(status=ResearchStatus.FAILED)
                    await session.execute(stmt)
                    await session.commit()

                # Publish error event
                await redis_client.publish_event(research_id, {
                    "event_type": "error",
                    "data": {"message": str(e), "recoverable": False},
                })

        except asyncio.CancelledError:
            logger.info("Worker cancelled")
            break
        except Exception as e:
            logger.error(f"Worker loop error: {e}", exc_info=True)
            await asyncio.sleep(5)  # Back off on unexpected errors

    await redis_client.disconnect()
    logger.info("Worker shut down cleanly.")


def main():
    """Entry point for the worker process."""
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        asyncio.run(process_queue())
    except KeyboardInterrupt:
        logger.info("Worker interrupted by keyboard.")


if __name__ == "__main__":
    main()
