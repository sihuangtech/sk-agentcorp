"""
SK AgentCorp — Audit Service

Records immutable audit trail entries for all significant system events.
"""

import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.audit import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """Service for recording and querying immutable audit logs."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        company_id: str,
        event_type: str,
        message: str,
        *,
        severity: str = "info",
        category: str = "system",
        actor_type: str = "system",
        actor_id: str = "",
        actor_name: str = "",
        details: dict | None = None,
        task_id: str | None = None,
        agent_id: str | None = None,
    ) -> AuditLog:
        """Record an immutable audit log entry."""
        entry = AuditLog(
            company_id=company_id,
            event_type=event_type,
            severity=severity,
            category=category,
            actor_type=actor_type,
            actor_id=actor_id,
            actor_name=actor_name,
            message=message,
            details=json.dumps(details or {}),
            task_id=task_id,
            agent_id=agent_id,
        )
        self.db.add(entry)
        await self.db.flush()
        logger.info(f"Audit [{severity}] [{event_type}]: {message}")
        return entry

    async def list_by_company(
        self,
        company_id: str,
        event_type: str | None = None,
        severity: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditLog]:
        """Query audit logs for a company with optional filters."""
        stmt = (
            select(AuditLog)
            .where(AuditLog.company_id == company_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if event_type:
            stmt = stmt.where(AuditLog.event_type == event_type)
        if severity:
            stmt = stmt.where(AuditLog.severity == severity)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_recent(self, company_id: str, limit: int = 20) -> list[AuditLog]:
        """Get most recent audit entries for activity feed."""
        return await self.list_by_company(company_id, limit=limit)
