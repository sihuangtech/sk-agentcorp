"""
SK AgentCorp — Task Service

Business logic for task lifecycle, Kanban management, and assignment.
"""

import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.task import Task, TaskDependency
from backend.schemas.task import TaskCreate, TaskResponse, TaskUpdate

logger = logging.getLogger(__name__)


class TaskService:
    """Service layer for task operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: TaskCreate) -> Task:
        """Create a new task and set up dependencies."""
        task = Task(
            company_id=data.company_id,
            title=data.title,
            description=data.description,
            priority=data.priority,
            category=data.category,
            acceptance_criteria=data.acceptance_criteria,
            assigned_agent_id=data.assigned_agent_id,
            requires_approval=data.requires_approval,
            estimated_cost_usd=data.estimated_cost_usd,
            timeout_seconds=data.timeout_seconds,
            max_retries=data.max_retries,
            status="backlog",
            kanban_column="backlog",
        )
        self.db.add(task)
        await self.db.flush()

        # Create dependency edges
        for dep_id in data.depends_on:
            dep = TaskDependency(task_id=task.id, depends_on_task_id=dep_id)
            self.db.add(dep)

        await self.db.flush()
        logger.info(f"Created task: {task.title} ({task.id})")
        return task

    async def get(self, task_id: str) -> Task | None:
        """Get a task by ID."""
        return await self.db.get(Task, task_id)

    async def list_by_company(
        self,
        company_id: str,
        status: str | None = None,
        limit: int = 100,
    ) -> list[Task]:
        """List tasks for a company, optionally filtered by status."""
        stmt = (
            select(Task)
            .where(Task.company_id == company_id)
            .order_by(Task.kanban_order, Task.created_at.desc())
            .limit(limit)
        )
        if status:
            stmt = stmt.where(Task.status == status)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, task_id: str, data: TaskUpdate) -> Task | None:
        """Update a task."""
        task = await self.get(task_id)
        if not task:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        # Sync kanban_column with status changes
        status_to_column = {
            "backlog": "backlog",
            "queued": "queued",
            "in_progress": "in_progress",
            "review": "review",
            "done": "done",
            "failed": "failed",
            "blocked": "blocked",
        }
        if "status" in update_data:
            task.kanban_column = status_to_column.get(task.status, task.kanban_column)
            if task.status == "in_progress" and not task.started_at:
                task.started_at = datetime.now(timezone.utc)
            elif task.status in ("done", "failed"):
                task.completed_at = datetime.now(timezone.utc)

        await self.db.flush()
        return task

    async def delete(self, task_id: str) -> bool:
        """Delete a task."""
        task = await self.get(task_id)
        if not task:
            return False
        await self.db.delete(task)
        await self.db.flush()
        return True

    async def get_ready_tasks(self, company_id: str) -> list[Task]:
        """
        Get tasks that are ready to execute:
        - Status is 'queued' or 'backlog'
        - All dependencies are completed
        - Not blocked or cancelled
        """
        stmt = select(Task).where(
            Task.company_id == company_id,
            Task.status.in_(["queued", "backlog"]),
        )
        result = await self.db.execute(stmt)
        tasks = list(result.scalars().all())

        ready = []
        for task in tasks:
            # Check all dependencies are done
            deps_stmt = select(TaskDependency).where(TaskDependency.task_id == task.id)
            deps_result = await self.db.execute(deps_stmt)
            deps = list(deps_result.scalars().all())

            all_deps_done = True
            for dep in deps:
                dep_task = await self.get(dep.depends_on_task_id)
                if dep_task and dep_task.status != "done":
                    all_deps_done = False
                    break

            if all_deps_done:
                ready.append(task)

        return ready

    async def get_stuck_tasks(self, company_id: str) -> list[Task]:
        """Get tasks that appear stuck (in_progress too long, or errored)."""
        stmt = select(Task).where(
            Task.company_id == company_id,
            Task.status.in_(["in_progress", "review"]),
        )
        result = await self.db.execute(stmt)
        tasks = list(result.scalars().all())

        stuck = []
        now = datetime.now(timezone.utc)
        for task in tasks:
            if task.started_at:
                elapsed = (now - task.started_at).total_seconds()
                if elapsed > task.timeout_seconds:
                    stuck.append(task)

        return stuck

    async def to_response(self, task: Task) -> TaskResponse:
        """Convert ORM model to API response."""
        deliverables = json.loads(task.deliverables) if task.deliverables else []
        return TaskResponse(
            id=task.id,
            company_id=task.company_id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            category=task.category,
            status=task.status,
            assigned_agent_id=task.assigned_agent_id,
            assigned_agent_name=task.assigned_agent_name,
            crew_id=task.crew_id,
            acceptance_criteria=task.acceptance_criteria,
            deliverables=deliverables,
            output=task.output,
            output_quality_score=task.output_quality_score,
            retry_count=task.retry_count,
            max_retries=task.max_retries,
            timeout_seconds=task.timeout_seconds,
            error_log=task.error_log,
            fallback_agent_id=task.fallback_agent_id,
            thread_id=task.thread_id,
            checkpoint_id=task.checkpoint_id,
            estimated_cost_usd=task.estimated_cost_usd,
            actual_cost_usd=task.actual_cost_usd,
            kanban_column=task.kanban_column,
            kanban_order=task.kanban_order,
            requires_approval=task.requires_approval,
            approval_status=task.approval_status,
            created_at=task.created_at,
            updated_at=task.updated_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
        )
