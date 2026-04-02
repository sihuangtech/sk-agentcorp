"""
SK AgentCorp — Budget Pydantic Schemas
"""

from datetime import datetime

from pydantic import BaseModel


class BudgetEntryCreate(BaseModel):
    """Schema for recording a budget entry."""
    company_id: str
    entry_type: str  # llm_call | tool_usage | manual_adjustment | refund
    description: str = ""
    amount_usd: float
    llm_provider: str = ""
    llm_model: str = ""
    tokens_input: int = 0
    tokens_output: int = 0
    task_id: str | None = None
    agent_id: str | None = None


class BudgetEntryResponse(BaseModel):
    """Schema for budget entry API responses."""
    id: str
    company_id: str
    entry_type: str
    description: str
    amount_usd: float
    llm_provider: str
    llm_model: str
    tokens_input: int
    tokens_output: int
    task_id: str | None
    agent_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class BudgetSummary(BaseModel):
    """Aggregated budget summary for a company."""
    company_id: str
    budget_cap_usd: float
    total_spent_usd: float
    remaining_usd: float
    utilization_pct: float
    is_over_budget: bool
    entries_count: int
    cost_by_type: dict[str, float] = {}
    cost_by_model: dict[str, float] = {}
    daily_spend: list[dict] = []
