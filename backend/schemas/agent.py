"""
SK AgentCorp — Agent Pydantic Schemas
"""

from datetime import datetime

from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    """Schema for creating or deploying a new agent."""
    company_id: str
    role_id: str  # References a YAML role definition
    name: str = Field(..., min_length=1, max_length=255)
    title: str = ""
    department: str = "general"
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    reports_to: str | None = None
    position_x: float = 0.0
    position_y: float = 0.0


class AgentUpdate(BaseModel):
    """Schema for updating an agent."""
    name: str | None = None
    title: str | None = None
    department: str | None = None
    llm_provider: str | None = None
    llm_model: str | None = None
    status: str | None = None
    status_message: str | None = None
    reports_to: str | None = None
    position_x: float | None = None
    position_y: float | None = None
    is_active: bool | None = None
    system_prompt: str | None = None
    tools: list[str] | None = None
    backstory: str | None = None


class AgentResponse(BaseModel):
    """Schema for agent API responses."""
    id: str
    company_id: str
    role_id: str
    name: str
    title: str
    department: str
    llm_provider: str
    llm_model: str
    status: str
    current_task_id: str | None
    status_message: str
    reports_to: str | None
    position_x: float
    position_y: float
    tasks_completed: int
    tasks_failed: int
    total_cost_usd: float
    is_active: bool
    system_prompt: str
    tools: list[str]
    backstory: str
    created_at: datetime
    updated_at: datetime
    last_active_at: datetime | None

    model_config = {"from_attributes": True}
