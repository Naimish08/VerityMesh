"""
Planner Agent Node.

Decomposes a research question into sub-questions and determines research strategy.
"""

import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from agents.state import ResearchState
from agents.prompts.planner import PLANNER_SYSTEM_PROMPT, PlannerOutput
from config import settings

logger = logging.getLogger("veritymesh.planner")


async def planner_node(state: ResearchState) -> dict:
    """
    Planner node: takes the research question and decomposes it into
    sub-questions with a research strategy.
    """
    question = state["question"]
    logger.info(f"Planning research for: {question[:100]}...")

    llm = ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.3,
    )
    structured_llm = llm.with_structured_output(PlannerOutput)

    messages = [
        ("system", PLANNER_SYSTEM_PROMPT),
        ("human", f"Research Question: {question}"),
    ]

    try:
        result = await structured_llm.ainvoke(messages)
        logger.info(f"Planner produced {len(result.sub_questions)} sub-questions")

        return {
            "sub_questions": result.sub_questions,
            "research_strategy": result.research_strategy,
            "required_source_types": result.required_source_types,
            "current_step": "researching",
        }
    except Exception as e:
        logger.error(f"Planner failed: {e}", exc_info=True)
        # Fallback: use the original question as the sole sub-question
        return {
            "sub_questions": [question],
            "research_strategy": "Direct research on the main question",
            "required_source_types": ["web"],
            "errors": [f"Planner error: {str(e)}"],
            "current_step": "researching",
        }
