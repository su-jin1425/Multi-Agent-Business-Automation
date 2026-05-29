from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db_session
from app.models.enums import UserRole
from app.schemas.ticket import TicketCreate, TicketRead, TicketUpdate
from app.services.ticket_service import TicketService


router = APIRouter()


@router.post("", response_model=TicketRead, status_code=201)
async def create_ticket(payload: TicketCreate, session: AsyncSession = Depends(get_db_session)) -> TicketRead:
    return await TicketService(session).create(payload)


@router.get("", response_model=list[TicketRead])
async def list_tickets(
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(get_current_user),
) -> list:
    return await TicketService(session).list()


@router.put("/{ticket_id}", response_model=TicketRead)
async def update_ticket(
    ticket_id: UUID,
    payload: TicketUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.SUPPORT_EXECUTIVE)),
) -> TicketRead:
    return await TicketService(session).update(ticket_id, payload)

