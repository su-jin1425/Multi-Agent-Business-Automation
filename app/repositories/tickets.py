from collections.abc import Sequence

from sqlalchemy import select

from app.models.enums import TicketStatus
from app.models.support_ticket import SupportTicket
from app.repositories.base import BaseRepository


class TicketRepository(BaseRepository[SupportTicket]):
    model = SupportTicket

    async def list_open(self) -> Sequence[SupportTicket]:
        result = await self.session.execute(
            select(SupportTicket).where(SupportTicket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
        )
        return result.scalars().all()

