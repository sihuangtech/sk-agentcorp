"""
SK AgentCorp — Agent ORM Model

Represents an AI agent assigned to a company, with a specific role,
LLM backend, and runtime status tracking.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Agent(Base):
    """An AI agent that fulfills a specific role within a company."""

    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    company_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # ── Role ─────────────────────────────────────────────────────────
    role_id: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "ceo", "frontend_dev"
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), default="")
    department: Mapped[str] = mapped_column(String(100), default="general")

    # ── LLM Config ───────────────────────────────────────────────────
    llm_provider: Mapped[str] = mapped_column(String(50), default="openai")
    llm_model: Mapped[str] = mapped_column(String(100), default="gpt-4o")

    # ── Status ───────────────────────────────────────────────────────
    status: Mapped[str] = mapped_column(
        String(20), default="idle"
    )  # idle | working | stuck | error | offline
    current_task_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    status_message: Mapped[str] = mapped_column(Text, default="")

    # ── Org Chart Position ───────────────────────────────────────────
    reports_to: Mapped[str | None] = mapped_column(String(36), nullable=True)  # Agent ID
    position_x: Mapped[float] = mapped_column(Float, default=0.0)
    position_y: Mapped[float] = mapped_column(Float, default=0.0)

    # ── Stats ────────────────────────────────────────────────────────
    tasks_completed: Mapped[int] = mapped_column(Integer, default=0)
    tasks_failed: Mapped[int] = mapped_column(Integer, default=0)
    total_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)

    # ── Config ───────────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    system_prompt: Mapped[str] = mapped_column(Text, default="")
    tools: Mapped[str] = mapped_column(Text, default="[]")  # JSON array of tool names
    backstory: Mapped[str] = mapped_column(Text, default="")

    # ── Timestamps ───────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
    last_active_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Relationships ────────────────────────────────────────────────
    company: Mapped["Company"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Company", back_populates="agents"
    )

    def __repr__(self) -> str:
        return f"<Agent {self.name} [{self.role_id}] ({self.id[:8]})>"
