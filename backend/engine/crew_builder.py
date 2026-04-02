"""
SK AgentCorp — Crew Builder

Dynamically assembles agent crews for task execution.
Matches tasks to the best available agents based on role, skills, and availability.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from backend.engine.shared_memory import SharedMemory
from backend.engine.workflow import run_task_workflow
from backend.models.agent import Agent
from backend.models.task import Task
from backend.services.agent_service import AgentService
from backend.services.audit_service import AuditService
from backend.services.budget_service import BudgetService
from backend.services.task_service import TaskService

logger = logging.getLogger(__name__)


class CrewBuilder:
    """
    Builds and dispatches agent crews to execute tasks.

    Responsibilities:
    - Match tasks to appropriate agents based on role/department
    - Check budget before execution
    - Run tasks through the LangGraph workflow
    - Update task and agent states after completion
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_service = TaskService(db)
        self.agent_service = AgentService(db)
        self.budget_service = BudgetService(db)
        self.audit_service = AuditService(db)

    async def process_ready_tasks(self, company_id: str) -> dict:
        """
        Main entry: find ready tasks, assign agents, and execute.

        Returns summary of actions taken.
        """
        summary = {"assigned": 0, "executed": 0, "skipped": 0, "budget_blocked": 0}

        # Get tasks ready for execution
        ready_tasks = await self.task_service.get_ready_tasks(company_id)
        if not ready_tasks:
            return summary

        # Get available agents
        available_agents = await self.agent_service.get_available_agents(company_id)
        if not available_agents:
            logger.info(f"[CrewBuilder] No available agents for company {company_id}")
            return summary

        for task in ready_tasks:
            # Skip tasks pending human approval
            if task.requires_approval and task.approval_status == "pending":
                summary["skipped"] += 1
                continue

            # Check budget
            has_budget = await self.budget_service.check_budget(
                company_id, task.estimated_cost_usd
            )
            if not has_budget:
                summary["budget_blocked"] += 1
                logger.warning(f"[CrewBuilder] Budget insufficient for task: {task.title}")
                continue

            # Find best matching agent
            agent = self._match_agent(task, available_agents)
            if not agent:
                summary["skipped"] += 1
                continue

            # Assign and execute
            await self._assign_and_execute(task, agent, company_id)
            summary["assigned"] += 1
            summary["executed"] += 1

            # Remove agent from available pool
            available_agents = [a for a in available_agents if a.id != agent.id]

        logger.info(f"[CrewBuilder] Company {company_id}: {summary}")
        return summary

    def _match_agent(self, task: Task, agents: list[Agent]) -> Agent | None:
        """
        Match a task to the best available agent.

        Priority:
        1. Agent specifically assigned to the task
        2. Agent matching task category/department
        3. Any available agent
        """
        # 1. Check if task has a pre-assigned agent
        if task.assigned_agent_id:
            for agent in agents:
                if agent.id == task.assigned_agent_id:
                    return agent

        # 2. Match by department/category
        category_to_dept = {
            "engineering": ["engineering", "devops", "data"],
            "marketing": ["marketing", "creative"],
            "sales": ["sales"],
            "product": ["product"],
            "operations": ["operations"],
            "general": [],  # Any agent can handle
        }

        preferred_depts = category_to_dept.get(task.category, [])
        if preferred_depts:
            for agent in agents:
                if agent.department in preferred_depts:
                    return agent

        # 3. Fallback: any available agent
        return agents[0] if agents else None

    async def _assign_and_execute(
        self, task: Task, agent: Agent, company_id: str
    ) -> None:
        """Assign an agent to a task and run the workflow."""

        # Update task state
        task.status = "in_progress"
        task.kanban_column = "in_progress"
        task.assigned_agent_id = agent.id
        task.assigned_agent_name = agent.name
        task.started_at = datetime.now(timezone.utc)

        # Update agent state
        agent.status = "working"
        agent.current_task_id = task.id
        agent.last_active_at = datetime.now(timezone.utc)

        await self.db.flush()

        # Log assignment
        await self.audit_service.log(
            company_id=company_id,
            event_type="task_assigned",
            message=f"Task '{task.title}' assigned to agent '{agent.name}'",
            category="task",
            task_id=task.id,
            agent_id=agent.id,
            actor_type="system",
            actor_name="CrewBuilder",
        )

        # Get shared memory context
        shared_mem = SharedMemory(self.db, company_id)
        context_data = await shared_mem.get_all()
        context_str = "\n".join(f"- {k}: {v[:200]}" for k, v in context_data.items()) if context_data else ""

        try:
            # Run the LangGraph workflow
            result = await run_task_workflow(
                task_id=task.id,
                task_title=task.title,
                task_description=task.description,
                acceptance_criteria=task.acceptance_criteria or "Complete the task as described.",
                agent_name=agent.name,
                agent_role=agent.title or agent.role_id,
                agent_system_prompt=agent.system_prompt or f"You are a professional {agent.role_id}.",
                llm_provider=agent.llm_provider,
                llm_model=agent.llm_model,
                shared_context=context_str,
                max_retries=task.max_retries,
            )

            # Update task with results
            task.output = result.get("output", "")
            task.output_quality_score = result.get("quality_score", 0.0)
            task.thread_id = result.get("thread_id", "")
            task.retry_count = result.get("retry_count", 0)

            if result["status"] == "done":
                task.status = "done"
                task.kanban_column = "done"
                task.completed_at = datetime.now(timezone.utc)
                agent.tasks_completed += 1

                # Store deliverable in shared memory
                await shared_mem.set(
                    f"task_output:{task.id}",
                    task.output[:1000],
                    agent_id=agent.id,
                    agent_name=agent.name,
                )

                await self.audit_service.log(
                    company_id=company_id,
                    event_type="task_completed",
                    message=f"Task '{task.title}' completed (quality: {task.output_quality_score:.2f})",
                    category="task",
                    task_id=task.id,
                    agent_id=agent.id,
                )
            else:
                task.status = "failed"
                task.kanban_column = "failed"
                task.completed_at = datetime.now(timezone.utc)
                task.error_log += "\n".join(result.get("errors", []))
                agent.tasks_failed += 1

                await self.audit_service.log(
                    company_id=company_id,
                    event_type="task_failed",
                    message=f"Task '{task.title}' failed after workflow execution",
                    severity="error",
                    category="task",
                    task_id=task.id,
                    agent_id=agent.id,
                )

        except Exception as e:
            logger.error(f"[CrewBuilder] Workflow error for task {task.id}: {e}")
            task.status = "failed"
            task.kanban_column = "failed"
            task.error_log += f"\nWorkflow error: {str(e)}"
            agent.tasks_failed += 1

        finally:
            # Release agent
            agent.status = "idle"
            agent.current_task_id = None
            await self.db.flush()
