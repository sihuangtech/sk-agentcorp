"""
SK AgentCorp — Tasks Router

REST API endpoints for task lifecycle, Kanban board, and approval workflows.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from backend.services.task_service import TaskService

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(data: TaskCreate, db: AsyncSession = Depends(get_db)):
    """Create a new task."""
    service = TaskService(db)
    task = await service.create(data)
    return await service.to_response(task)


@router.get("/company/{company_id}", response_model=list[TaskResponse])
async def list_tasks(
    company_id: str,
    status: str | None = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List tasks for a company, optionally filtered by status."""
    service = TaskService(db)
    tasks = await service.list_by_company(company_id, status=status, limit=limit)
    return [await service.to_response(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific task."""
    service = TaskService(db)
    task = await service.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return await service.to_response(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, data: TaskUpdate, db: AsyncSession = Depends(get_db)):
    """Update a task."""
    service = TaskService(db)
    task = await service.update(task_id, data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return await service.to_response(task)


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a task."""
    service = TaskService(db)
    if not await service.delete(task_id):
        raise HTTPException(status_code=404, detail="Task not found")


@router.post("/{task_id}/approve")
async def approve_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Approve a task pending human review."""
    service = TaskService(db)
    task = await service.update(task_id, TaskUpdate(approval_status="approved", status="queued"))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "approved"}


@router.post("/{task_id}/reject")
async def reject_task(task_id: str, reason: str = "", db: AsyncSession = Depends(get_db)):
    """Reject a task pending human review."""
    service = TaskService(db)
    task = await service.update(task_id, TaskUpdate(approval_status="rejected", status="cancelled"))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "rejected", "reason": reason}
