from app.agents.analytics import AnalyticsAgent
from app.agents.base import BusinessAgent
from app.agents.finance import FinanceAgent
from app.agents.operations import OperationsAgent
from app.agents.support import SupportAgent
from app.models.enums import AgentType


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[AgentType, BusinessAgent] = {
            AgentType.FINANCE: FinanceAgent(),
            AgentType.ANALYTICS: AnalyticsAgent(),
            AgentType.SUPPORT: SupportAgent(),
            AgentType.OPERATIONS: OperationsAgent(),
        }

    def get(self, agent_type: AgentType) -> BusinessAgent:
        return self._agents[agent_type]

    def all(self) -> list[BusinessAgent]:
        return list(self._agents.values())


agent_registry = AgentRegistry()
