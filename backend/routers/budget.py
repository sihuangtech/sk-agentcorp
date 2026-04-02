"""
SK AgentCorp — Budget Router

REST API endpoints for budget tracking, cost analysis, and spend history.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.schemas.budget import BudgetEntryResponse, BudgetSummary
from backend.services.budget_service import BudgetService

router = APIRouter(prefix="/api/budget", tags=["budget"])


@router.get("/{company_id}/summary", response_model=BudgetSummary)
async def get_budget_summary(company_id: str, db: AsyncSession = Depends(get_db)):
    """Get aggregated budget summary for a company."""
    service = BudgetService(db)
    return await service.get_summary(company_id)


@router.get("/{company_id}/entries", response_model=list[BudgetEntryResponse])
async def list_budget_entries(
    company_id: str, limit: int = 50, db: AsyncSession = Depends(get_db)
):
    """List recent budget entries for a company."""
    service = BudgetService(db)
    entries = await service.list_entries(company_id, limit=limit)
    return [
        BudgetEntryResponse(
            id=e.id,
            company_id=e.company_id,
            entry_type=e.entry_type,
            description=e.description,
            amount_usd=e.amount_usd,
            llm_provider=e.llm_provider,
            llm_model=e.llm_model,
            tokens_input=e.tokens_input,
            tokens_output=e.tokens_output,
            task_id=e.task_id,
            agent_id=e.agent_id,
            created_at=e.created_at,
        )
        for e in entries
    ]
