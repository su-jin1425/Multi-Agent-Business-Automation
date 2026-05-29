from typing import Any, TypedDict

from app.models.enums import AgentType, WorkflowStatus, WorkflowType


class WorkflowState(TypedDict, total=False):
    workflow_id: str
    workflow_type: WorkflowType
    status: WorkflowStatus
    input_payload: dict[str, Any]
    agent_results: list[dict[str, Any]]
    next_agents: list[AgentType]
    errors: list[str]

