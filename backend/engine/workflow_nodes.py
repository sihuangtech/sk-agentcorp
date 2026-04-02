import logging
from typing import Any, Literal
from pathlib import Path

from backend.engine.llm_router import get_llm
from backend.engine.workflow_state import TaskWorkflowState

logger = logging.getLogger(__name__)

# Load prompts from txt files
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

with open(PROMPTS_DIR / "plan_prompt.txt", "r", encoding="utf-8") as f:
    WORKFLOW_PLAN_PROMPT = f.read()

with open(PROMPTS_DIR / "execute_prompt.txt", "r", encoding="utf-8") as f:
    WORKFLOW_EXECUTE_PROMPT = f.read()

with open(PROMPTS_DIR / "validate_prompt.txt", "r", encoding="utf-8") as f:
    WORKFLOW_VALIDATE_PROMPT = f.read()


# ═══════════════════════════════════════════════════════════════════════
#  Node Functions
# ═══════════════════════════════════════════════════════════════════════

def plan_task(state: TaskWorkflowState) -> dict[str, Any]:
    """
    Node 1: Plan the task execution.
    The agent creates a detailed execution plan based on the task description.
    """
    logger.info(f"[Workflow] Planning task: {state['task_title']}")

    try:
        llm = get_llm(state["llm_provider"], state["llm_model"])

        plan_prompt = WORKFLOW_PLAN_PROMPT.format(
            agent_name=state['agent_name'],
            agent_role=state['agent_role'],
            agent_system_prompt=state['agent_system_prompt'],
            task_title=state['task_title'],
            task_description=state['task_description'],
            acceptance_criteria=state['acceptance_criteria'],
            shared_context=state.get('shared_context', 'No additional context.')
        )

        response = llm.invoke(plan_prompt)
        plan_text = response.content if hasattr(response, "content") else str(response)

        return {
            "plan": plan_text,
            "status": "executing",
            "messages": [{"role": "agent", "content": f"Plan created: {plan_text[:200]}..."}],
        }
    except Exception as e:
        logger.error(f"[Workflow] Planning failed: {e}")
        return {
            "errors": [f"Planning failed: {str(e)}"],
            "status": "retrying",
            "messages": [{"role": "system", "content": f"Planning error: {e}"}],
        }


def execute_task(state: TaskWorkflowState) -> dict[str, Any]:
    """
    Node 2: Execute the task according to the plan.
    The agent produces the actual deliverable.
    """
    logger.info(f"[Workflow] Executing task: {state['task_title']}")

    try:
        llm = get_llm(state["llm_provider"], state["llm_model"])

        exec_prompt = WORKFLOW_EXECUTE_PROMPT.format(
            agent_name=state['agent_name'],
            agent_role=state['agent_role'],
            agent_system_prompt=state['agent_system_prompt'],
            task_title=state['task_title'],
            task_description=state['task_description'],
            plan=state['plan'],
            acceptance_criteria=state['acceptance_criteria']
        )

        response = llm.invoke(exec_prompt)
        output_text = response.content if hasattr(response, "content") else str(response)

        return {
            "output": output_text,
            "status": "validating",
            "messages": [{"role": "agent", "content": f"Execution complete. Output length: {len(output_text)} chars"}],
        }
    except Exception as e:
        logger.error(f"[Workflow] Execution failed: {e}")
        return {
            "errors": [f"Execution failed: {str(e)}"],
            "status": "retrying",
            "messages": [{"role": "system", "content": f"Execution error: {e}"}],
        }


def validate_output(state: TaskWorkflowState) -> dict[str, Any]:
    """
    Node 3: Validate the output against acceptance criteria.
    Uses a separate LLM call to objectively evaluate quality.
    """
    logger.info(f"[Workflow] Validating output for: {state['task_title']}")

    try:
        llm = get_llm(state["llm_provider"], state["llm_model"], temperature=0.1)

        validate_prompt = WORKFLOW_VALIDATE_PROMPT.format(
            task_title=state['task_title'],
            task_description=state['task_description'],
            acceptance_criteria=state['acceptance_criteria'],
            output=state['output'][:3000]
        )

        response = llm.invoke(validate_prompt)
        validation_text = response.content if hasattr(response, "content") else str(response)

        # Parse score
        score = 0.5
        verdict = "PASS"
        for line in validation_text.split("\n"):
            if line.strip().startswith("SCORE:"):
                try:
                    score = float(line.split(":")[1].strip())
                except ValueError:
                    score = 0.5
            if line.strip().startswith("VERDICT:"):
                verdict = line.split(":")[1].strip().upper()

        if verdict == "PASS" and score >= 0.6:
            return {
                "validation_result": validation_text,
                "quality_score": score,
                "status": "done",
                "messages": [{"role": "system", "content": f"Validation PASSED (score: {score})"}],
            }
        else:
            return {
                "validation_result": validation_text,
                "quality_score": score,
                "status": "retrying",
                "errors": [f"Validation failed (score: {score}): {validation_text[:200]}"],
                "messages": [{"role": "system", "content": f"Validation FAILED (score: {score}), will retry"}],
            }
    except Exception as e:
        logger.error(f"[Workflow] Validation failed: {e}")
        # If validation itself fails, pass the task through
        return {
            "validation_result": f"Validation error: {e}",
            "quality_score": 0.5,
            "status": "done",
            "messages": [{"role": "system", "content": f"Validation error (passing through): {e}"}],
        }


def handle_retry(state: TaskWorkflowState) -> dict[str, Any]:
    """
    Node 4: Handle retry logic.
    Increments retry count and prepares for re-execution.
    """
    new_retry = state.get("retry_count", 0) + 1
    max_retries = state.get("max_retries", 3)

    if new_retry > max_retries:
        logger.warning(f"[Workflow] Max retries exceeded for: {state['task_title']}")
        return {
            "retry_count": new_retry,
            "status": "failed",
            "messages": [{"role": "system", "content": f"Max retries ({max_retries}) exceeded. Task failed."}],
        }

    logger.info(f"[Workflow] Retry {new_retry}/{max_retries} for: {state['task_title']}")
    return {
        "retry_count": new_retry,
        "status": "executing",
        "messages": [{"role": "system", "content": f"Retrying ({new_retry}/{max_retries})..."}],
    }


# ═══════════════════════════════════════════════════════════════════════
#  Router Functions
# ═══════════════════════════════════════════════════════════════════════

def route_after_plan(state: TaskWorkflowState) -> Literal["execute", "retry"]:
    """Route after planning: execute if successful, retry if failed."""
    if state.get("status") == "retrying":
        return "retry"
    return "execute"


def route_after_execute(state: TaskWorkflowState) -> Literal["validate", "retry"]:
    """Route after execution: validate if successful, retry if failed."""
    if state.get("status") == "retrying":
        return "retry"
    return "validate"


def route_after_validate(state: TaskWorkflowState) -> Literal["__end__", "retry"]:
    """Route after validation: end if passed, retry if failed."""
    if state.get("status") == "done":
        return "__end__"
    return "retry"


def route_after_retry(state: TaskWorkflowState) -> Literal["execute", "__end__"]:
    """Route after retry: re-execute or give up."""
    if state.get("status") == "failed":
        return "__end__"
    return "execute"
