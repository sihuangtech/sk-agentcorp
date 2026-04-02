"""
SK AgentCorp — Budget Service

Tracks LLM costs, enforces budget caps, and auto-pauses companies on overspend.
"""

import logging
from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.budget import BudgetEntry
from backend.models.company import Company
from backend.schemas.budget import BudgetEntryCreate, BudgetEntryResponse, BudgetSummary

logger = logging.getLogger(__name__)


class BudgetService:
    """Service layer for budget tracking and enforcement."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_cost(self, data: BudgetEntryCreate) -> BudgetEntry:
        """Record a new cost entry and update company's total spend."""
        entry = BudgetEntry(
            company_id=data.company_id,
            entry_type=data.entry_type,
            description=data.description,
            amount_usd=data.amount_usd,
            llm_provider=data.llm_provider,
            llm_model=data.llm_model,
            tokens_input=data.tokens_input,
            tokens_output=data.tokens_output,
            task_id=data.task_id,
            agent_id=data.agent_id,
        )
        self.db.add(entry)

        # Update company's cumulative spend
        company = await self.db.get(Company, data.company_id)
        if company:
            company.budget_spent_usd += data.amount_usd

            # Auto-pause if budget exceeded
            if company.budget_spent_usd >= company.budget_cap_usd:
                company.is_paused = True
                company.pause_reason = (
                    f"Budget cap exceeded: ${company.budget_spent_usd:.2f} / "
                    f"${company.budget_cap_usd:.2f}"
                )
                logger.warning(f"Company {company.name} paused: budget exceeded")

        await self.db.flush()
        return entry

    async def get_summary(self, company_id: str) -> BudgetSummary:
        """Get aggregated budget summary for a company."""
        company = await self.db.get(Company, company_id)
        if not company:
            return BudgetSummary(
                company_id=company_id,
                budget_cap_usd=0, total_spent_usd=0,
                remaining_usd=0, utilization_pct=0,
                is_over_budget=False, entries_count=0,
            )

        # Total entries
        count_stmt = select(func.count(BudgetEntry.id)).where(
            BudgetEntry.company_id == company_id
        )
        count_result = await self.db.execute(count_stmt)
        entries_count = count_result.scalar() or 0

        # Cost by type
        entries_stmt = select(BudgetEntry).where(BudgetEntry.company_id == company_id)
        entries_result = await self.db.execute(entries_stmt)
        entries = list(entries_result.scalars().all())

        cost_by_type: dict[str, float] = defaultdict(float)
        cost_by_model: dict[str, float] = defaultdict(float)
        for e in entries:
            cost_by_type[e.entry_type] += e.amount_usd
            if e.llm_model:
                cost_by_model[e.llm_model] += e.amount_usd

        remaining = company.budget_cap_usd - company.budget_spent_usd
        utilization = (
            (company.budget_spent_usd / company.budget_cap_usd * 100)
            if company.budget_cap_usd > 0
            else 0
        )

        return BudgetSummary(
            company_id=company_id,
            budget_cap_usd=company.budget_cap_usd,
            total_spent_usd=company.budget_spent_usd,
            remaining_usd=max(0, remaining),
            utilization_pct=round(utilization, 2),
            is_over_budget=company.budget_spent_usd >= company.budget_cap_usd,
            entries_count=entries_count,
            cost_by_type=dict(cost_by_type),
            cost_by_model=dict(cost_by_model),
        )

    async def list_entries(
        self, company_id: str, limit: int = 50
    ) -> list[BudgetEntry]:
        """List recent budget entries for a company."""
        stmt = (
            select(BudgetEntry)
            .where(BudgetEntry.company_id == company_id)
            .order_by(BudgetEntry.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def check_budget(self, company_id: str, estimated_cost: float = 0) -> bool:
        """Check if a company has enough budget for an operation."""
        company = await self.db.get(Company, company_id)
        if not company:
            return False
        return (company.budget_spent_usd + estimated_cost) < company.budget_cap_usd
