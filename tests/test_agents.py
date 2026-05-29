import pytest

from app.agents.base import AgentContext
from app.agents.registry import agent_registry
from app.models.enums import AgentType


@pytest.mark.asyncio
async def test_finance_agent_detects_anomalies() -> None:
    agent = agent_registry.get(AgentType.FINANCE)
    result = await agent.execute(
        AgentContext(
            task="Analyze expenses",
            payload={"expenses": [{"amount": 10}, {"amount": 20}, {"amount": 500}]},
        )
    )

    assert result.agent_type == AgentType.FINANCE
    assert result.data["total_expense"] == 530
    assert result.data["anomalies"]


@pytest.mark.asyncio
async def test_support_agent_escalates_refund_issue() -> None:
    agent = agent_registry.get(AgentType.SUPPORT)
    result = await agent.execute(AgentContext(task="Triage", payload={"issue": "I need a refund for a failed order"}))

    assert result.data["sentiment"] == "negative"
    assert result.data["escalate"] is True
    assert AgentType.OPERATIONS in result.delegated_to

