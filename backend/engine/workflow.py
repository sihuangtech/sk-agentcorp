"""
SK AgentCorp — LangGraph Task Workflow

Stateful workflow using LangGraph StateGraph with checkpoint persistence.
Each task runs through: plan → execute → validate → deliver.
Includes retry, timeout, fallback, and structured output validation.
"""

import logging
import uuid
from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from backend.engine.workflow_state import TaskWorkflowState
from backend.engine.workflow_nodes import (
    plan_task,
    execute_task,
    validate_output,
    handle_retry,
    route_after_plan,
    route_after_execute,
    route_after_validate,
    route_after_retry,
)

logger = logging.getLogger(__name__)

# ── Checkpointer (in-memory for dev, swap to PostgresSaver for production) ──
_checkpointer = MemorySaver()

# ═══════════════════════════════════════════════════════════════════════
#  Graph Builder
# ═══════════════════════════════════════════════════════════════════════

def build_task_workflow() -> Any:
    """
    Build and compile the LangGraph task workflow.

    Flow: plan → execute → validate → (done or retry → execute)

    Returns a compiled graph with checkpoint persistence.
    """
    builder = StateGraph(TaskWorkflowState)

    # Add nodes
    builder.add_node("plan", plan_task)
    builder.add_node("execute", execute_task)
    builder.add_node("validate", validate_output)
    builder.add_node("retry", handle_retry)

    # Entry point
    builder.add_edge(START, "plan")

    # Conditional edges
    builder.add_conditional_edges("plan", route_after_plan, {
        "execute": "execute",
        "retry": "retry",
    })
    builder.add_conditional_edges("execute", route_after_execute, {
        "validate": "validate",
        "retry": "retry",
    })
    builder.add_conditional_edges("validate", route_after_validate, {
        "__end__": END,
        "retry": "retry",
    })
    builder.add_conditional_edges("retry", route_after_retry, {
        "execute": "execute",
        "__end__": END,
    })

    # Compile with checkpoint persistence
    graph = builder.compile(checkpointer=_checkpointer)
    logger.info("[Workflow] Task workflow graph compiled successfully")
    return graph


# ── Singleton ────────────────────────────────────────────────────────
_workflow_graph = None

def get_task_workflow() -> Any:
    """Get or create the singleton task workflow graph."""
    global _workflow_graph
    if _workflow_graph is None:
        _workflow_graph = build_task_workflow()
    return _workflow_graph


async def run_task_workflow(
    task_id: str,
    task_title: str,
    task_description: str,
    acceptance_criteria: str,
    agent_name: str,
    agent_role: str,
    agent_system_prompt: str,
    llm_provider: str,
    llm_model: str,
    shared_context: str = "",
    max_retries: int = 3,
) -> dict[str, Any]:
    """
    Execute a task through the complete LangGraph workflow.

    Returns the final state including output, quality score, and status.
    """
    graph = get_task_workflow()
    thread_id = f"task-{task_id}-{uuid.uuid4().hex[:8]}"

    initial_state: TaskWorkflowState = {
        "task_id": task_id,
        "task_title": task_title,
        "task_description": task_description,
        "acceptance_criteria": acceptance_criteria,
        "agent_name": agent_name,
        "agent_role": agent_role,
        "agent_system_prompt": agent_system_prompt,
        "llm_provider": llm_provider,
        "llm_model": llm_model,
        "messages": [],
        "plan": "",
        "output": "",
        "validation_result": "",
        "quality_score": 0.0,
        "retry_count": 0,
        "max_retries": max_retries,
        "errors": [],
        "status": "planning",
        "shared_context": shared_context,
        "total_tokens": 0,
        "estimated_cost": 0.0,
    }

    config = {"configurable": {"thread_id": thread_id}}

    logger.info(f"[Workflow] Starting task workflow: {task_title} (thread: {thread_id})")

    try:
        # Run the graph — invoke returns the final state
        final_state = await graph.ainvoke(initial_state, config=config)

        logger.info(
            f"[Workflow] Task completed: {task_title} "
            f"(status: {final_state.get('status')}, "
            f"score: {final_state.get('quality_score')}, "
            f"retries: {final_state.get('retry_count')})"
        )

        return {
            "thread_id": thread_id,
            "status": final_state.get("status", "failed"),
            "output": final_state.get("output", ""),
            "quality_score": final_state.get("quality_score", 0.0),
            "retry_count": final_state.get("retry_count", 0),
            "errors": final_state.get("errors", []),
            "plan": final_state.get("plan", ""),
            "validation_result": final_state.get("validation_result", ""),
        }

    except Exception as e:
        logger.error(f"[Workflow] Fatal error in task workflow: {e}")
        return {
            "thread_id": thread_id,
            "status": "failed",
            "output": "",
            "quality_score": 0.0,
            "retry_count": 0,
            "errors": [str(e)],
            "plan": "",
            "validation_result": "",
        }
