"""
Research models: ResearchRun and ResearchTask.
"""

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin, TimestampMixin


class ResearchStatus(str, enum.Enum):
    PENDING = "pending"
    PLANNING = "planning"
    RESEARCHING = "researching"
    EXTRACTING = "extracting"
    VERIFYING = "verifying"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchDepth(str, enum.Enum):
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"


class ResearchRun(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "research_runs"

    question: Mapped[str] = mapped_column(String(2000), index=True)
    status: Mapped[ResearchStatus] = mapped_column(
        Enum(ResearchStatus, name="research_status", values_callable=lambda e: [x.value for x in e]),
        default=ResearchStatus.PENDING,
    )
    depth: Mapped[ResearchDepth] = mapped_column(
        Enum(ResearchDepth, name="research_depth", values_callable=lambda e: [x.value for x in e]),
        default=ResearchDepth.STANDARD,
    )
    config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    stats: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    tasks: Mapped[list["ResearchTask"]] = relationship(back_populates="research_run", cascade="all, delete-orphan")


class ResearchTask(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "research_tasks"

    research_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("research_runs.id", ondelete="CASCADE"),
        index=True,
    )
    task_type: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(2000))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    research_run: Mapped["ResearchRun"] = relationship(back_populates="tasks")
