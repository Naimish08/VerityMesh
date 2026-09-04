"""
LangGraph agent pipeline for VerityMesh research workflow.

Phase 1 flow: START → planner → web_researcher → synthesizer → END
"""

import json
import logging
import time
import uuid
from datetime import datetime

from langgraph.graph import StateGraph, START, END

from agents.state import ResearchState
from agents.nodes.planner import planner_node
from agents.nodes.web_researcher import web_researcher_node
from agents.nodes.synthesizer import synthesizer_node
from database.connection import AsyncSessionLocal
from database.models import ResearchRun, ResearchStatus

logger = logging.getLogger("veritymesh.graph")


def build_research_graph() -> StateGraph:
    """Build and compile the Phase 1 research StateGraph."""
    builder = StateGraph(ResearchState)

    builder.add_node("planner", planner_node)
    builder.add_node("web_researcher", web_researcher_node)
    builder.add_node("synthesizer", synthesizer_node)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "web_researcher")
    builder.add_edge("web_researcher", "synthesizer")
    builder.add_edge("synthesizer", END)

    return builder.compile()


async def run_research(
    research_id: str,
    question: str,
    config: dict,
    redis_client,
) -> None:
    """
    Execute the full research pipeline for a given question.
    
    This function is called by the worker process. It:
    1. Compiles the LangGraph
    2. Streams execution, publishing events to Redis for SSE
    3. Updates the research run status in the database
    """
    graph = build_research_graph()
    start_time = time.time()

    async def publish(event_type: str, data: dict):
        """Publish an event to Redis pub/sub for SSE streaming."""
        await redis_client.publish_event(research_id, {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        })

    # Update status to PLANNING
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select, update
        stmt = update(ResearchRun).where(
            ResearchRun.id == uuid.UUID(research_id)
        ).values(status=ResearchStatus.PLANNING)
        await session.execute(stmt)
        await session.commit()

    await publish("status_change", {"status": "planning"})

    initial_state: ResearchState = {
        "research_id": research_id,
        "question": question,
        "config": config,
        "sub_questions": [],
        "research_strategy": "",
        "required_source_types": [],
        "sources": [],
        "chunks": [],
        "claims": [],
        "errors": [],
        "report": "",
        "citations": [],
        "current_step": "planning",
        "iteration": 0,
    }

    try:
        # Stream through the graph
        async for event in graph.astream(
            initial_state,
            stream_mode="updates",
        ):
            for node_name, node_output in event.items():
                if node_name == "__end__":
                    continue

                logger.info(f"Node '{node_name}' completed")

                # Publish node completion event
                step_map = {
                    "planner": "planning",
                    "web_researcher": "researching",
                    "synthesizer": "synthesizing",
                }
                step = step_map.get(node_name, node_name)

                # Update DB status based on the NEXT step
                status_map = {
                    "planner": ResearchStatus.RESEARCHING,
                    "web_researcher": ResearchStatus.SYNTHESIZING,
                    "synthesizer": ResearchStatus.COMPLETED,
                }
                new_status = status_map.get(node_name)

                if node_name == "planner":
                    sub_questions = node_output.get("sub_questions", [])
                    await publish("planning", {
                        "sub_questions": sub_questions,
                        "strategy": node_output.get("research_strategy", ""),
                    })

                elif node_name == "web_researcher":
                    sources = node_output.get("sources", [])
                    await publish("research_complete", {
                        "sources_count": len(sources),
                    })

                elif node_name == "synthesizer":
                    await publish("report_ready", {
                        "report_length": len(node_output.get("report", "")),
                    })

                # Update status
                if new_status:
                    async with AsyncSessionLocal() as session:
                        stmt = update(ResearchRun).where(
                            ResearchRun.id == uuid.UUID(research_id)
                        ).values(status=new_status)
                        await session.execute(stmt)
                        await session.commit()

                    await publish("status_change", {"status": new_status.value})

        # Calculate stats
        elapsed = time.time() - start_time

        # Save final result
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            stmt = select(ResearchRun).where(
                ResearchRun.id == uuid.UUID(research_id)
            )
            result = await session.execute(stmt)
            run = result.scalar_one()

            # Get the final state from the last event
            run.status = ResearchStatus.COMPLETED
            run.stats = {
                "duration_ms": int(elapsed * 1000),
                "sources_analyzed": len(initial_state.get("sources", [])),
                "tokens_used": 0,
            }
            await session.commit()

        await publish("complete", {
            "stats": {
                "duration_ms": int(elapsed * 1000),
            }
        })

    except Exception as e:
        logger.error(f"Research pipeline failed: {e}", exc_info=True)

        async with AsyncSessionLocal() as session:
            stmt = update(ResearchRun).where(
                ResearchRun.id == uuid.UUID(research_id)
            ).values(status=ResearchStatus.FAILED)
            await session.execute(stmt)
            await session.commit()

        await publish("error", {
            "message": str(e),
            "recoverable": False,
        })
