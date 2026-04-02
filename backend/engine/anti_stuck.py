"""
SK AgentCorp — Anti-Stuck Engine

The most critical component: ensures tasks never get permanently stuck.

Strategies:
1. Timeout detection — tasks running too long are killed and retried
2. Automatic retry — up to N retries with exponential backoff intent
3. Supervisor fallback — escalate to a supervisor agent after max retries
4. Structured output validation — reject garbage outputs
5. Heartbeat monitoring — detect unresponsive agents
"""

import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import get_settings
from backend.models.agent import Agent
from backend.models.task import Task
from backend.services.audit_service import AuditService
from backend.services.task_service import TaskService

logger = logging.getLogger(__name__)


class AntiStuckEngine:
    """
    Monitors and recovers stuck tasks and agents.

    Called periodically by the heartbeat scheduler to scan for problems
    and apply automatic remediation.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()
        self.task_service = TaskService(db)
        self.audit_service = AuditService(db)

    async def scan_and_recover(self, company_id: str) -> dict:
        """
        Main entry point: scan for stuck tasks and attempt recovery.

        Returns summary of actions taken.
        """
        summary = {
            "timed_out": 0,
            "retried": 0,
            "failed_permanently": 0,
            "escalated": 0,
            "agents_reset": 0,
        }

        # 1. Find timed-out tasks
        stuck_tasks = await self.task_service.get_stuck_tasks(company_id)

        for task in stuck_tasks:
            summary["timed_out"] += 1
            action = await self._handle_stuck_task(task, company_id)
            summary[action] = summary.get(action, 0) + 1

        # 2. Reset stuck agents (working status but no active task)
        await self._reset_stuck_agents(company_id, summary)

        if any(v > 0 for v in summary.values()):
            logger.info(f"[AntiStuck] Company {company_id}: {summary}")

        return summary

    async def _handle_stuck_task(self, task: Task, company_id: str) -> str:
        """Handle a single stuck task. Returns the action taken."""
        elapsed = 0.0
        if task.started_at:
            elapsed = (datetime.now(timezone.utc) - task.started_at).total_seconds()

        logger.warning(
            f"[AntiStuck] Task stuck: {task.title} "
            f"(elapsed: {elapsed:.0f}s, retries: {task.retry_count}/{task.max_retries})"
        )

        if task.retry_count < task.max_retries:
            # ── Retry ────────────────────────────────────────────────
            task.retry_count += 1
            task.status = "queued"
            task.kanban_column = "queued"
            task.started_at = None  # Reset timer
            task.error_log += f"\n[{datetime.now(timezone.utc).isoformat()}] Timed out after {elapsed:.0f}s. Retry {task.retry_count}/{task.max_retries}."

            # Release the assigned agent
            if task.assigned_agent_id:
                agent = await self.db.get(Agent, task.assigned_agent_id)
                if agent:
                    agent.status = "idle"
                    agent.current_task_id = None

            await self.audit_service.log(
                company_id=company_id,
                event_type="task_retry",
                message=f"Task '{task.title}' timed out. Retry {task.retry_count}/{task.max_retries}.",
                severity="warning",
                category="task",
                task_id=task.id,
            )

            await self.db.flush()
            return "retried"

        else:
            # ── Try supervisor fallback ──────────────────────────────
            if task.fallback_agent_id:
                task.assigned_agent_id = task.fallback_agent_id
                task.status = "queued"
                task.kanban_column = "queued"
                task.retry_count = 0  # Reset for the fallback agent
                task.started_at = None
                task.error_log += f"\n[{datetime.now(timezone.utc).isoformat()}] Escalated to supervisor fallback agent."

                await self.audit_service.log(
                    company_id=company_id,
                    event_type="task_escalated",
                    message=f"Task '{task.title}' escalated to supervisor after {task.max_retries} retries.",
                    severity="warning",
                    category="task",
                    task_id=task.id,
                )

                await self.db.flush()
                return "escalated"
            else:
                # ── Permanent failure ────────────────────────────────
                task.status = "failed"
                task.kanban_column = "failed"
                task.completed_at = datetime.now(timezone.utc)
                task.error_log += f"\n[{datetime.now(timezone.utc).isoformat()}] Permanently failed after {task.max_retries} retries."

                # Release agent
                if task.assigned_agent_id:
                    agent = await self.db.get(Agent, task.assigned_agent_id)
                    if agent:
                        agent.status = "idle"
                        agent.current_task_id = None
                        agent.tasks_failed += 1

                await self.audit_service.log(
                    company_id=company_id,
                    event_type="task_failed",
                    message=f"Task '{task.title}' permanently failed after all retries exhausted.",
                    severity="error",
                    category="task",
                    task_id=task.id,
                )

                await self.db.flush()
                return "failed_permanently"

    async def _reset_stuck_agents(self, company_id: str, summary: dict) -> None:
        """Reset agents that show 'working' status but have no active task."""
        from sqlalchemy import select

        stmt = select(Agent).where(
            Agent.company_id == company_id,
            Agent.status == "working",
        )
        result = await self.db.execute(stmt)
        agents = list(result.scalars().all())

        for agent in agents:
            # Check if the agent's current task is actually still in progress
            if agent.current_task_id:
                task = await self.db.get(Task, agent.current_task_id)
                if task and task.status == "in_progress":
                    continue  # Agent is genuinely working

            # Agent is stuck — reset to idle
            agent.status = "idle"
            agent.current_task_id = None
            agent.status_message = "Reset by anti-stuck engine"
            summary["agents_reset"] += 1

            logger.info(f"[AntiStuck] Reset stuck agent: {agent.name}")

        await self.db.flush()
