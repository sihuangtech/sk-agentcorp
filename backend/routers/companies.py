"""
SK AgentCorp — Companies Router

REST API endpoints for company CRUD, goal management, and lifecycle.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.schemas.company import CompanyCreate, CompanyDashboardStats, CompanyResponse, CompanyUpdate
from backend.services.company_service import CompanyService

router = APIRouter(prefix="/api/companies", tags=["companies"])


@router.post("", response_model=CompanyResponse, status_code=201)
async def create_company(data: CompanyCreate, db: AsyncSession = Depends(get_db)):
    """Create a new virtual company."""
    service = CompanyService(db)
    company = await service.create(data)
    return await service.to_response(company)


@router.get("", response_model=list[CompanyResponse])
async def list_companies(active_only: bool = False, db: AsyncSession = Depends(get_db)):
    """List all companies."""
    service = CompanyService(db)
    companies = await service.list_all(active_only=active_only)
    return [await service.to_response(c) for c in companies]


@router.get("/stats", response_model=CompanyDashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get aggregated dashboard statistics across all companies."""
    service = CompanyService(db)
    return await service.get_dashboard_stats()


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific company by ID."""
    service = CompanyService(db)
    company = await service.get(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return await service.to_response(company)


@router.patch("/{company_id}", response_model=CompanyResponse)
async def update_company(company_id: str, data: CompanyUpdate, db: AsyncSession = Depends(get_db)):
    """Update a company."""
    service = CompanyService(db)
    company = await service.update(company_id, data)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return await service.to_response(company)


@router.delete("/{company_id}", status_code=204)
async def delete_company(company_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a company and all related data."""
    service = CompanyService(db)
    if not await service.delete(company_id):
        raise HTTPException(status_code=404, detail="Company not found")


@router.post("/{company_id}/pause")
async def pause_company(company_id: str, reason: str = "", db: AsyncSession = Depends(get_db)):
    """Pause a company's autonomous operations."""
    service = CompanyService(db)
    company = await service.pause_company(company_id, reason)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"status": "paused", "reason": reason}


@router.post("/{company_id}/resume")
async def resume_company(company_id: str, db: AsyncSession = Depends(get_db)):
    """Resume a paused company."""
    service = CompanyService(db)
    company = await service.update(company_id, CompanyUpdate(is_paused=False, pause_reason=""))
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"status": "resumed"}
