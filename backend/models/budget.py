"""
SK AgentCorp — Budget Entry ORM Model

Tracks every financial transaction (LLM API costs, tool usage, etc.)
to enable real-time budget monitoring and automatic pause on overspend.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class BudgetEntry(Base):
    """A single financial transaction record."""

    __tablename__ = "budget_entries"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    company_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # ── Transaction ──────────────────────────────────────────────────
    entry_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # llm_call | tool_usage | manual_adjustment | refund
    description: Mapped[str] = mapped_column(Text, default="")
    amount_usd: Mapped[float] = mapped_column(Float, nullable=False)

    # ── LLM Details ──────────────────────────────────────────────────
    llm_provider: Mapped[str] = mapped_column(String(50), default="")
    llm_model: Mapped[str] = mapped_column(String(100), default="")
    tokens_input: Mapped[int] = mapped_column(default=0)
    tokens_output: Mapped[int] = mapped_column(default=0)

    # ── Reference ────────────────────────────────────────────────────
    task_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    agent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # ── Timestamp ────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, index=True
    )

    # ── Relationships ────────────────────────────────────────────────
    company: Mapped["Company"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Company", back_populates="budget_entries"
    )

    def __repr__(self) -> str:
        return f"<BudgetEntry ${self.amount_usd:.4f} [{self.entry_type}]>"
