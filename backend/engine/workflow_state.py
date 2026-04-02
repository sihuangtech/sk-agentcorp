from typing import Annotated, Any, TypedDict
import operator

class TaskWorkflowState(TypedDict):
    """Shared state for the task execution workflow."""
    # Task info
    task_id: str
    task_title: str
    task_description: str
    acceptance_criteria: str

    # Agent info
    agent_name: str
    agent_role: str
    agent_system_prompt: str
    llm_provider: str
    llm_model: str

    # Execution state
    messages: Annotated[list[dict[str, Any]], operator.add]
    plan: str
    output: str
    validation_result: str
    quality_score: float

    # Anti-stuck tracking
    retry_count: int
    max_retries: int
    errors: Annotated[list[str], operator.add]
    status: str  # planning | executing | validating | delivering | done | failed | retrying

    # Shared context
    shared_context: str  # Serialized shared memory snapshot

    # Cost tracking
    total_tokens: int
    estimated_cost: float
