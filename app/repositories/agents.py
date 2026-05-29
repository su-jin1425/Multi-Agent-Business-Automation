from sqlalchemy import select

from app.models.agent import Agent
from app.models.enums import AgentType
from app.repositories.base import BaseRepository


class AgentRepository(BaseRepository[Agent]):
    model = Agent

    async def get_by_type(self, agent_type: AgentType) -> Agent | None:
        result = await self.session.execute(select(Agent).where(Agent.agent_type == agent_type))
        return result.scalar_one_or_none()

