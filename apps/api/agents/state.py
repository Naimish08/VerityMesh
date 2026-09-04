"""
LangGraph State definition for the research pipeline.
"""

from typing import Annotated, Any, TypedDict


def merge_lists(left: list | None, right: list | None) -> list:
    """Reducer that merges two lists, handling None gracefully."""
    if left is None:
        left = []
    if right is None:
        right = []
    return left + right


class ResearchState(TypedDict, total=False):
    """
    Shared state across all nodes in the research graph.
    
    Using total=False so nodes only need to return the fields they update.
    """
    # Core inputs (set at initialization)
    research_id: str
    question: str
    config: dict[str, Any]

    # Planner outputs
    sub_questions: list[str]
    research_strategy: str
    required_source_types: list[str]

    # Research outputs (use Annotated reducers for list merging)
    sources: Annotated[list[dict[str, Any]], merge_lists]
    chunks: Annotated[list[dict[str, Any]], merge_lists]
    claims: Annotated[list[dict[str, Any]], merge_lists]
    errors: Annotated[list[str], merge_lists]

    # Synthesis outputs
    report: str
    citations: list[dict[str, Any]]

    # Tracking
    current_step: str
    iteration: int
