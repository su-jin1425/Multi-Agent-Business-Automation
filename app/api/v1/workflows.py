from uuid import UUID

from fastapi import APIRouter, Depends, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, redis_dependency, require_roles
from app.db.session import get_db_session
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.workflow import WorkflowCreate, WorkflowRead, WorkflowTriggerResponse, WorkflowUpdate
from app.services.workflow_service import WorkflowService
from app.tasks import execute_workflow_task


router = APIRouter()


def service(session: AsyncSession, redis: Redis) -> WorkflowService:
    return WorkflowService(session, redis)


@router.post("", response_model=WorkflowRead, status_code=201)
async def create_workflow(
    payload: WorkflowCreate,
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(redis_dependency),
    user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ANALYST)),
) -> WorkflowRead:
    return await service(session, redis).create(payload, user.id)


@router.get("", response_model=list[WorkflowRead])
async def list_workflows(
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(redis_dependency),
    _: User = Depends(get_current_user),
) -> list:
    return await service(session, redis).list()


@router.get("/{workflow_id}", response_model=WorkflowRead)
async def get_workflow(
    workflow_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(redis_dependency),
    _: User = Depends(get_current_user),
) -> WorkflowRead:
    return await service(session, redis).get(workflow_id)


@router.put("/{workflow_id}", response_model=WorkflowRead)
async def update_workflow(
    workflow_id: UUID,
    payload: WorkflowUpdate,
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(redis_dependency),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
) -> WorkflowRead:
    return await service(session, redis).update(workflow_id, payload)


@router.delete("/{workflow_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def delete_workflow(
    workflow_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(redis_dependency),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
) -> MessageResponse:
    await service(session, redis).delete(workflow_id)
    return MessageResponse(message="Workflow deleted")


@router.post("/{workflow_id}/trigger", response_model=WorkflowTriggerResponse)
async def trigger_workflow(
    workflow_id: UUID,
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ANALYST)),
) -> WorkflowTriggerResponse:
    celery_result = execute_workflow_task.delay(str(workflow_id))
    return WorkflowTriggerResponse(
        workflow_id=workflow_id,
        status="pending",
        celery_task_id=celery_result.id,
        message="Workflow queued for distributed execution",
    )


@router.post("/{workflow_id}/execute", response_model=WorkflowRead)
async def execute_workflow_inline(
    workflow_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(redis_dependency),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ANALYST)),
) -> WorkflowRead:
    return await service(session, redis).execute(workflow_id)


@router.post("/{workflow_id}/pause", response_model=WorkflowRead)
async def pause_workflow(
    workflow_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(redis_dependency),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
) -> WorkflowRead:
    return await service(session, redis).pause(workflow_id)


@router.post("/{workflow_id}/resume", response_model=WorkflowRead)
async def resume_workflow(
    workflow_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(redis_dependency),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
) -> WorkflowRead:
    return await service(session, redis).resume(workflow_id)


@router.post("/{workflow_id}/retry", response_model=WorkflowRead)
async def retry_workflow(
    workflow_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(redis_dependency),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
) -> WorkflowRead:
    return await service(session, redis).retry(workflow_id)

