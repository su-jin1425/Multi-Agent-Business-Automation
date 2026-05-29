from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentContext
from app.agents.registry import agent_registry
from app.core.exceptions import NotFoundError
from app.models.enums import AgentType, TicketStatus
from app.models.support_ticket import SupportTicket
from app.repositories.tickets import TicketRepository
from app.schemas.ticket import TicketCreate, TicketUpdate


class TicketService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.tickets = TicketRepository(session)

    async def create(self, payload: TicketCreate) -> SupportTicket:
        support_agent = agent_registry.get(AgentType.SUPPORT)
        result = await support_agent.execute(AgentContext(task="Classify support ticket", payload=payload.model_dump()))
        data = result.data
        ticket = await self.tickets.create(
            customer_name=payload.customer_name,
            issue=payload.issue,
            sentiment=data.get("sentiment", "neutral"),
            assigned_agent=AgentType.SUPPORT.value,
            status=TicketStatus.ESCALATED if data.get("escalate") else TicketStatus.OPEN,
            response_draft=data.get("response_draft"),
        )
        await self.session.commit()
        return ticket

    async def list(self) -> list[SupportTicket]:
        return list(await self.tickets.list(limit=100))

    async def update(self, ticket_id, payload: TicketUpdate) -> SupportTicket:
        ticket = await self.tickets.get(ticket_id)
        if not ticket:
            raise NotFoundError("Support ticket")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(ticket, key, value)
        await self.session.commit()
        await self.session.refresh(ticket)
        return ticket

