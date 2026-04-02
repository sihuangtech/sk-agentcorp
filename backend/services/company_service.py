"""
SK AgentCorp — Company Service

Business logic for company CRUD, goal management, and lifecycle operations.
"""

import json
import logging
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.agent import Agent
from backend.models.company import Company
from backend.models.task import Task
from backend.schemas.company import CompanyCreate, CompanyDashboardStats, CompanyResponse, CompanyUpdate

logger = logging.getLogger(__name__)


class CompanyService:
    """Service layer for company operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: CompanyCreate) -> Company:
        """Create a new company."""
        company = Company(
            name=data.name,
            description=data.description,
            mission=data.mission,
            vision=data.vision,
            goals=json.dumps(data.goals),
            budget_cap_usd=data.budget_cap_usd,
            template_id=data.template_id,
        )
        self.db.add(company)
        await self.db.flush()
        logger.info(f"Created company: {company.name} ({company.id})")
        return company

    async def get(self, company_id: str) -> Company | None:
        """Get a company by ID."""
        return await self.db.get(Company, company_id)

    async def list_all(self, active_only: bool = False) -> list[Company]:
        """List all companies, optionally filtering to active only."""
        stmt = select(Company).order_by(Company.created_at.desc())
        if active_only:
            stmt = stmt.where(Company.is_active == True)  # noqa: E712
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, company_id: str, data: CompanyUpdate) -> Company | None:
        """Update a company's fields."""
        company = await self.get(company_id)
        if not company:
            return None

        update_data = data.model_dump(exclude_unset=True)
        if "goals" in update_data and update_data["goals"] is not None:
            update_data["goals"] = json.dumps(update_data["goals"])

        for field, value in update_data.items():
            setattr(company, field, value)

        await self.db.flush()
        logger.info(f"Updated company: {company.name} ({company.id})")
        return company

    async def delete(self, company_id: str) -> bool:
        """Delete a company and all related data."""
        company = await self.get(company_id)
        if not company:
            return False
        await self.db.delete(company)
        await self.db.flush()
        logger.info(f"Deleted company: {company.name} ({company_id})")
        return True

    async def update_heartbeat(self, company_id: str) -> None:
        """Record that the heartbeat ran for this company."""
        company = await self.get(company_id)
        if company:
            company.last_heartbeat_at = datetime.now(timezone.utc)
            await self.db.flush()

    async def pause_company(self, company_id: str, reason: str = "") -> Company | None:
        """Pause a company (e.g., budget exceeded)."""
        company = await self.get(company_id)
        if company:
            company.is_paused = True
            company.pause_reason = reason
            await self.db.flush()
            logger.warning(f"Paused company {company.name}: {reason}")
        return company

    async def to_response(self, company: Company) -> CompanyResponse:
        """Convert ORM model to response schema with computed fields."""
        # Count agents
        agent_count_stmt = select(func.count(Agent.id)).where(Agent.company_id == company.id)
        agent_result = await self.db.execute(agent_count_stmt)
        agent_count = agent_result.scalar() or 0

        # Count tasks
        task_count_stmt = select(func.count(Task.id)).where(Task.company_id == company.id)
        task_result = await self.db.execute(task_count_stmt)
        task_count = task_result.scalar() or 0

        # Count active tasks
        active_stmt = select(func.count(Task.id)).where(
            Task.company_id == company.id,
            Task.status.in_(["queued", "in_progress", "review"]),
        )
        active_result = await self.db.execute(active_stmt)
        active_task_count = active_result.scalar() or 0

        goals = json.loads(company.goals) if company.goals else []

        return CompanyResponse(
            id=company.id,
            name=company.name,
            description=company.description,
            mission=company.mission,
            vision=company.vision,
            goals=goals,
            budget_cap_usd=company.budget_cap_usd,
            budget_spent_usd=company.budget_spent_usd,
            is_active=company.is_active,
            is_paused=company.is_paused,
            pause_reason=company.pause_reason,
            template_id=company.template_id,
            created_at=company.created_at,
            updated_at=company.updated_at,
            last_heartbeat_at=company.last_heartbeat_at,
            agent_count=agent_count,
            task_count=task_count,
            active_task_count=active_task_count,
        )

    async def get_dashboard_stats(self) -> CompanyDashboardStats:
        """Get aggregated statistics for the main dashboard."""
        companies = await self.list_all()

        total_agents = 0
        active_agents = 0
        total_tasks = 0
        completed_tasks = 0
        in_progress_tasks = 0
        failed_tasks = 0
        total_spent = 0.0
        total_cap = 0.0

        for c in companies:
            total_cap += c.budget_cap_usd
            total_spent += c.budget_spent_usd

            # Count agents per company
            agent_stmt = select(func.count(Agent.id)).where(Agent.company_id == c.id)
            r = await self.db.execute(agent_stmt)
            ac = r.scalar() or 0
            total_agents += ac

            active_stmt = select(func.count(Agent.id)).where(
                Agent.company_id == c.id, Agent.status != "offline"
            )
            r = await self.db.execute(active_stmt)
            active_agents += r.scalar() or 0

            # Count tasks per company
            for status, counter_name in [
                (None, "total"),
                ("done", "completed"),
                ("in_progress", "in_progress"),
                ("failed", "failed"),
            ]:
                stmt = select(func.count(Task.id)).where(Task.company_id == c.id)
                if status:
                    stmt = stmt.where(Task.status == status)
                r = await self.db.execute(stmt)
                count = r.scalar() or 0
                if counter_name == "total":
                    total_tasks += count
                elif counter_name == "completed":
                    completed_tasks += count
                elif counter_name == "in_progress":
                    in_progress_tasks += count
                elif counter_name == "failed":
                    failed_tasks += count

        return CompanyDashboardStats(
            total_companies=len(companies),
            active_companies=sum(1 for c in companies if c.is_active and not c.is_paused),
            total_agents=total_agents,
            active_agents=active_agents,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            in_progress_tasks=in_progress_tasks,
            failed_tasks=failed_tasks,
            total_budget_spent=total_spent,
            total_budget_cap=total_cap,
        )
