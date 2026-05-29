from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_roles
from app.core.exceptions import NotFoundError
from app.db.session import get_db_session
from app.models.enums import UserRole
from app.repositories.agents import AgentRepository
from app.schemas.agent import AgentExecuteRequest, AgentExecuteResponse, AgentRead
from app.services.agent_service import AgentService

router = APIRouter()


@router.get("", response_model=list[AgentRead])
async def list_agents(
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(get_current_user),
) -> list:
    return await AgentService(session).list_agents()


@router.get("/{agent_id}", response_model=AgentRead)
async def get_agent(
    agent_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(get_current_user),
) -> AgentRead:
    agent = await AgentRepository(session).get(agent_id)
    if not agent:
        raise NotFoundError("Agent")
    return agent


@router.post("/execute", response_model=AgentExecuteResponse)
async def execute_agent(
    payload: AgentExecuteRequest,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ANALYST, UserRole.SUPPORT_EXECUTIVE)),
) -> AgentExecuteResponse:
    return await AgentService(session).execute(payload)
