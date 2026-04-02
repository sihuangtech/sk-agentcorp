"""
SK AgentCorp — Agent Service

Business logic for agent lifecycle, role assignment, and status management.
"""

import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.agent import Agent
from backend.schemas.agent import AgentCreate, AgentResponse, AgentUpdate

logger = logging.getLogger(__name__)


class AgentService:
    """Service layer for agent operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: AgentCreate) -> Agent:
        """Deploy a new agent to a company."""
        agent = Agent(
            company_id=data.company_id,
            role_id=data.role_id,
            name=data.name,
            title=data.title,
            department=data.department,
            llm_provider=data.llm_provider,
            llm_model=data.llm_model,
            reports_to=data.reports_to,
            position_x=data.position_x,
            position_y=data.position_y,
        )
        self.db.add(agent)
        await self.db.flush()
        logger.info(f"Deployed agent: {agent.name} [{agent.role_id}] to company {agent.company_id}")
        return agent

    async def get(self, agent_id: str) -> Agent | None:
        """Get an agent by ID."""
        return await self.db.get(Agent, agent_id)

    async def list_by_company(self, company_id: str, active_only: bool = False) -> list[Agent]:
        """List all agents for a company."""
        stmt = select(Agent).where(Agent.company_id == company_id).order_by(Agent.created_at)
        if active_only:
            stmt = stmt.where(Agent.is_active == True)  # noqa: E712
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, agent_id: str, data: AgentUpdate) -> Agent | None:
        """Update an agent's properties."""
        agent = await self.get(agent_id)
        if not agent:
            return None

        update_data = data.model_dump(exclude_unset=True)
        if "tools" in update_data and update_data["tools"] is not None:
            update_data["tools"] = json.dumps(update_data["tools"])

        for field, value in update_data.items():
            setattr(agent, field, value)

        await self.db.flush()
        return agent

    async def delete(self, agent_id: str) -> bool:
        """Remove an agent."""
        agent = await self.get(agent_id)
        if not agent:
            return False
        await self.db.delete(agent)
        await self.db.flush()
        logger.info(f"Removed agent: {agent.name} ({agent_id})")
        return True

    async def set_status(self, agent_id: str, status: str, message: str = "") -> None:
        """Update agent's operational status."""
        agent = await self.get(agent_id)
        if agent:
            agent.status = status
            agent.status_message = message
            await self.db.flush()

    async def get_available_agents(self, company_id: str) -> list[Agent]:
        """Get agents that are idle and available for work."""
        stmt = select(Agent).where(
            Agent.company_id == company_id,
            Agent.is_active == True,  # noqa: E712
            Agent.status == "idle",
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def to_response(self, agent: Agent) -> AgentResponse:
        """Convert ORM model to API response."""
        tools = json.loads(agent.tools) if agent.tools else []
        return AgentResponse(
            id=agent.id,
            company_id=agent.company_id,
            role_id=agent.role_id,
            name=agent.name,
            title=agent.title,
            department=agent.department,
            llm_provider=agent.llm_provider,
            llm_model=agent.llm_model,
            status=agent.status,
            current_task_id=agent.current_task_id,
            status_message=agent.status_message,
            reports_to=agent.reports_to,
            position_x=agent.position_x,
            position_y=agent.position_y,
            tasks_completed=agent.tasks_completed,
            tasks_failed=agent.tasks_failed,
            total_cost_usd=agent.total_cost_usd,
            is_active=agent.is_active,
            system_prompt=agent.system_prompt,
            tools=tools,
            backstory=agent.backstory,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
            last_active_at=agent.last_active_at,
        )
