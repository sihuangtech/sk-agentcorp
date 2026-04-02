"""
SK AgentCorp — Dashboard Router

Aggregated endpoints for the web dashboard, including stats,
activity feed, role registry, and system controls.
"""

import json

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.engine.heartbeat import trigger_heartbeat_now
from backend.engine.llm_router import get_available_providers
from backend.roles.loader import get_role_registry
from backend.services.audit_service import AuditService
from backend.services.company_service import CompanyService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get global dashboard statistics."""
    service = CompanyService(db)
    stats = await service.get_dashboard_stats()
    return stats


@router.get("/activity/{company_id}")
async def get_activity_feed(company_id: str, limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Get recent activity feed for a company."""
    audit = AuditService(db)
    entries = await audit.get_recent(company_id, limit=limit)
    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "severity": e.severity,
            "category": e.category,
            "actor_type": e.actor_type,
            "actor_name": e.actor_name,
            "message": e.message,
            "details": json.loads(e.details) if e.details else {},
            "task_id": e.task_id,
            "agent_id": e.agent_id,
            "created_at": e.created_at.isoformat(),
        }
        for e in entries
    ]


@router.get("/audit/{company_id}")
async def get_audit_logs(
    company_id: str,
    event_type: str | None = None,
    severity: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Get audit logs with filtering."""
    audit = AuditService(db)
    entries = await audit.list_by_company(
        company_id, event_type=event_type, severity=severity, limit=limit, offset=offset
    )
    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "severity": e.severity,
            "category": e.category,
            "actor_type": e.actor_type,
            "actor_name": e.actor_name,
            "message": e.message,
            "details": json.loads(e.details) if e.details else {},
            "task_id": e.task_id,
            "agent_id": e.agent_id,
            "created_at": e.created_at.isoformat(),
        }
        for e in entries
    ]


@router.get("/roles")
async def list_roles():
    """List all available roles from the YAML registry."""
    registry = get_role_registry()
    return registry.list_roles()


@router.get("/roles/{role_id}")
async def get_role(role_id: str):
    """Get a specific role definition."""
    registry = get_role_registry()
    role = registry.get_role(role_id)
    if not role:
        return {"error": "Role not found"}
    return role


@router.get("/providers")
async def list_providers():
    """List configured LLM providers and their status."""
    return get_available_providers()


@router.post("/heartbeat/trigger")
async def trigger_heartbeat():
    """Manually trigger a heartbeat cycle."""
    result = await trigger_heartbeat_now()
    return result
