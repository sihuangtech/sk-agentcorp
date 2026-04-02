"""
SK AgentCorp — Task ORM Model

Represents a unit of work within the company, tracked through
its full lifecycle with retry/fallback state for the anti-stuck engine.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Task(Base):
    """A task in the company workflow with full lifecycle tracking."""

    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    company_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # ── Task Definition ──────────────────────────────────────────────
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    priority: Mapped[str] = mapped_column(
        String(20), default="medium"
    )  # critical | high | medium | low
    category: Mapped[str] = mapped_column(String(100), default="general")

    # ── Status ───────────────────────────────────────────────────────
    status: Mapped[str] = mapped_column(
        String(30), default="backlog", index=True
    )  # backlog | queued | in_progress | review | done | failed | blocked | cancelled

    # ── Assignment ───────────────────────────────────────────────────
    assigned_agent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    assigned_agent_name: Mapped[str] = mapped_column(String(255), default="")
    crew_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # ── Acceptance Criteria ──────────────────────────────────────────
    acceptance_criteria: Mapped[str] = mapped_column(Text, default="")
    deliverables: Mapped[str] = mapped_column(Text, default="[]")  # JSON array

    # ── Result ───────────────────────────────────────────────────────
    output: Mapped[str] = mapped_column(Text, default="")
    output_quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── Anti-Stuck ───────────────────────────────────────────────────
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=600)
    error_log: Mapped[str] = mapped_column(Text, default="")
    fallback_agent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # ── LangGraph ────────────────────────────────────────────────────
    thread_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    checkpoint_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ── Cost ─────────────────────────────────────────────────────────
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    actual_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)

    # ── Kanban ───────────────────────────────────────────────────────
    kanban_column: Mapped[str] = mapped_column(String(50), default="backlog")
    kanban_order: Mapped[int] = mapped_column(Integer, default=0)

    # ── Human Approval ───────────────────────────────────────────────
    requires_approval: Mapped[bool] = mapped_column(default=False)
    approval_status: Mapped[str] = mapped_column(
        String(20), default="none"
    )  # none | pending | approved | rejected

    # ── Timestamps ───────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Relationships ────────────────────────────────────────────────
    company: Mapped["Company"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Company", back_populates="tasks"
    )
    dependencies: Mapped[list["TaskDependency"]] = relationship(
        "TaskDependency",
        foreign_keys="TaskDependency.task_id",
        back_populates="task",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Task {self.title[:40]} [{self.status}] ({self.id[:8]})>"


class TaskDependency(Base):
    """Tracks dependencies between tasks (DAG edges)."""

    __tablename__ = "task_dependencies"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    task_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    depends_on_task_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )

    task: Mapped["Task"] = relationship(
        "Task", foreign_keys=[task_id], back_populates="dependencies"
    )
