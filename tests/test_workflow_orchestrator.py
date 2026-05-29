import pytest

from app.models.enums import WorkflowStatus, WorkflowType
from app.workflows.langgraph_orchestrator import LangGraphWorkflowOrchestrator


@pytest.mark.asyncio
async def test_hybrid_workflow_runs_multiple_agents() -> None:
    orchestrator = LangGraphWorkflowOrchestrator()
    state = await orchestrator.execute(
        {
            "workflow_id": "test",
            "workflow_type": WorkflowType.HYBRID,
            "status": WorkflowStatus.PENDING,
            "input_payload": {
                "expenses": [{"amount": 100}],
                "metrics": {"jan": 1, "feb": 2},
                "issue": "late invoice",
                "tasks": [{"name": "close books", "priority": 1}],
            },
            "agent_results": [],
        }
    )

    assert state["status"] == WorkflowStatus.COMPLETED
    assert len(state["agent_results"]) >= 4

