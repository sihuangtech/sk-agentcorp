"""
SK AgentCorp — Audit Log ORM Model

Immutable audit trail for all significant actions in the system.
Every agent action, budget change, approval, and system event is logged.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AuditLog(Base):
    """Immutable audit record — never updated or deleted."""

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    company_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # ── Event ────────────────────────────────────────────────────────
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # e.g. task_created, task_completed, budget_exceeded, agent_stuck, approval_requested
    severity: Mapped[str] = mapped_column(
        String(20), default="info"
    )  # info | warning | error | critical
    category: Mapped[str] = mapped_column(
        String(50), default="system"
    )  # system | agent | task | budget | governance

    # ── Actor ────────────────────────────────────────────────────────
    actor_type: Mapped[str] = mapped_column(
        String(20), default="system"
    )  # system | agent | human
    actor_id: Mapped[str] = mapped_column(String(36), default="")
    actor_name: Mapped[str] = mapped_column(String(255), default="")

    # ── Details ──────────────────────────────────────────────────────
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[str] = mapped_column(Text, default="{}")  # JSON blob

    # ── References ───────────────────────────────────────────────────
    task_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    agent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # ── Timestamp (immutable) ────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, index=True
    )

    # ── Relationships ────────────────────────────────────────────────
    company: Mapped["Company"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Company", back_populates="audit_logs"
    )

    def __repr__(self) -> str:
        return f"<AuditLog [{self.event_type}] {self.message[:50]}>"
