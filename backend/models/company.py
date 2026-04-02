"""
SK AgentCorp — Company ORM Model

Represents a virtual company managed by Agent crews.
Supports multi-company setups with independent goals and budgets.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Company(Base):
    """A virtual company that runs autonomously via AI agents."""

    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    mission: Mapped[str] = mapped_column(Text, default="")
    vision: Mapped[str] = mapped_column(Text, default="")

    # ── Goals ────────────────────────────────────────────────────────
    goals: Mapped[str] = mapped_column(Text, default="[]")  # JSON array of goals

    # ── Budget ───────────────────────────────────────────────────────
    budget_cap_usd: Mapped[float] = mapped_column(Float, default=1000.0)
    budget_spent_usd: Mapped[float] = mapped_column(Float, default=0.0)

    # ── Status ───────────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_paused: Mapped[bool] = mapped_column(Boolean, default=False)
    pause_reason: Mapped[str] = mapped_column(String(500), default="")

    # ── Template ─────────────────────────────────────────────────────
    template_id: Mapped[str] = mapped_column(String(100), default="custom")

    # ── Timestamps ───────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Relationships ────────────────────────────────────────────────
    agents: Mapped[list["Agent"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Agent", back_populates="company", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["Task"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Task", back_populates="company", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "AuditLog", back_populates="company", cascade="all, delete-orphan"
    )
    budget_entries: Mapped[list["BudgetEntry"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "BudgetEntry", back_populates="company", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Company {self.name} ({self.id[:8]})>"
