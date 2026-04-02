"""
SK AgentCorp — Task Pydantic Schemas
"""

from datetime import datetime

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    company_id: str
    title: str = Field(..., min_length=1, max_length=500)
    description: str = ""
    priority: str = "medium"
    category: str = "general"
    acceptance_criteria: str = ""
    assigned_agent_id: str | None = None
    depends_on: list[str] = Field(default_factory=list)  # Task IDs
    requires_approval: bool = False
    estimated_cost_usd: float = 0.0
    timeout_seconds: int = 600
    max_retries: int = 3


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    category: str | None = None
    status: str | None = None
    assigned_agent_id: str | None = None
    acceptance_criteria: str | None = None
    output: str | None = None
    output_quality_score: float | None = None
    kanban_column: str | None = None
    kanban_order: int | None = None
    approval_status: str | None = None
    requires_approval: bool | None = None


class TaskResponse(BaseModel):
    """Schema for task API responses."""
    id: str
    company_id: str
    title: str
    description: str
    priority: str
    category: str
    status: str
    assigned_agent_id: str | None
    assigned_agent_name: str
    crew_id: str | None
    acceptance_criteria: str
    deliverables: list[str]
    output: str
    output_quality_score: float | None
    retry_count: int
    max_retries: int
    timeout_seconds: int
    error_log: str
    fallback_agent_id: str | None
    thread_id: str | None
    checkpoint_id: str | None
    estimated_cost_usd: float
    actual_cost_usd: float
    kanban_column: str
    kanban_order: int
    requires_approval: bool
    approval_status: str
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    completed_at: datetime | None

    model_config = {"from_attributes": True}
