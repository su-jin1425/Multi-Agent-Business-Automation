import time
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentContext
from app.agents.registry import agent_registry
from app.models.agent import Agent
from app.models.enums import AgentStatus
from app.monitoring.metrics import agent_response_time
from app.repositories.agents import AgentRepository
from app.schemas.agent import AgentExecuteRequest, AgentExecuteResponse


class AgentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.agents = AgentRepository(session)

    async def ensure_default_agents(self) -> None:
        for business_agent in agent_registry.all():
            existing = await self.agents.get_by_type(business_agent.agent_type)
            if not existing:
                await self.agents.create(
                    agent_name=business_agent.name,
                    agent_type=business_agent.agent_type,
                    status=AgentStatus.IDLE,
                    capabilities=business_agent.capabilities,
                    last_active=datetime.now(UTC),
                )
        await self.session.commit()

    async def list_agents(self) -> list[Agent]:
        await self.ensure_default_agents()
        return list(await self.agents.list(limit=100))

    async def execute(self, payload: AgentExecuteRequest) -> AgentExecuteResponse:
        started = time.perf_counter()

        agent = agent_registry.get(payload.agent_type)
        context = AgentContext(task=payload.task, payload=payload.context)

        result = await agent.execute(context)

        agent_response_time.labels(
            agent_type=payload.agent_type.value
        ).observe(time.perf_counter() - started)

        db_agent = await self.agents.get_by_type(payload.agent_type)
        if db_agent:
            db_agent.status = AgentStatus.IDLE
            db_agent.last_active = datetime.now(UTC)

        await self.session.commit()

        return AgentExecuteResponse(
            agent_type=result.agent_type,
            result=result.model_dump(mode="json"),
            delegated_to=[agent_type.value for agent_type in result.delegated_to],
        )
