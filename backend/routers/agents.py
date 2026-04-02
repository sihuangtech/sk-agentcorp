"""
SK AgentCorp — Agents Router

REST API endpoints for agent deployment, management, and org chart.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.schemas.agent import AgentCreate, AgentResponse, AgentUpdate
from backend.services.agent_service import AgentService

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.post("", response_model=AgentResponse, status_code=201)
async def deploy_agent(data: AgentCreate, db: AsyncSession = Depends(get_db)):
    """Deploy a new agent to a company."""
    service = AgentService(db)
    agent = await service.create(data)
    return await service.to_response(agent)


@router.get("/company/{company_id}", response_model=list[AgentResponse])
async def list_agents(company_id: str, active_only: bool = False, db: AsyncSession = Depends(get_db)):
    """List all agents for a company."""
    service = AgentService(db)
    agents = await service.list_by_company(company_id, active_only=active_only)
    return [await service.to_response(a) for a in agents]


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific agent."""
    service = AgentService(db)
    agent = await service.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return await service.to_response(agent)


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, data: AgentUpdate, db: AsyncSession = Depends(get_db)):
    """Update an agent's configuration."""
    service = AgentService(db)
    agent = await service.update(agent_id, data)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return await service.to_response(agent)


@router.delete("/{agent_id}", status_code=204)
async def remove_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Remove an agent from a company."""
    service = AgentService(db)
    if not await service.delete(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
