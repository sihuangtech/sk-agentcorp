"""
SK AgentCorp — Company Pydantic Schemas
"""

from datetime import datetime

from pydantic import BaseModel, Field


class CompanyCreate(BaseModel):
    """Schema for creating a new company."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    mission: str = ""
    vision: str = ""
    goals: list[str] = Field(default_factory=list)
    budget_cap_usd: float = Field(default=1000.0, ge=0)
    template_id: str = "custom"


class CompanyUpdate(BaseModel):
    """Schema for updating a company."""
    name: str | None = None
    description: str | None = None
    mission: str | None = None
    vision: str | None = None
    goals: list[str] | None = None
    budget_cap_usd: float | None = Field(default=None, ge=0)
    is_active: bool | None = None
    is_paused: bool | None = None
    pause_reason: str | None = None


class CompanyResponse(BaseModel):
    """Schema for company API responses."""
    id: str
    name: str
    description: str
    mission: str
    vision: str
    goals: list[str]
    budget_cap_usd: float
    budget_spent_usd: float
    is_active: bool
    is_paused: bool
    pause_reason: str
    template_id: str
    created_at: datetime
    updated_at: datetime
    last_heartbeat_at: datetime | None
    agent_count: int = 0
    task_count: int = 0
    active_task_count: int = 0

    model_config = {"from_attributes": True}


class CompanyDashboardStats(BaseModel):
    """Aggregated stats for the dashboard."""
    total_companies: int = 0
    active_companies: int = 0
    total_agents: int = 0
    active_agents: int = 0
    total_tasks: int = 0
    completed_tasks: int = 0
    in_progress_tasks: int = 0
    failed_tasks: int = 0
    total_budget_spent: float = 0.0
    total_budget_cap: float = 0.0
