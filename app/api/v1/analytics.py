from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import redis_dependency, require_roles
from app.db.session import get_db_session
from app.models.enums import UserRole
from app.schemas.analytics import AgentPerformance, OverviewMetrics, WorkflowMetrics
from app.services.analytics_service import AnalyticsService
from app.services.notification_service import NotificationService

router = APIRouter()


def analytics_service(session: AsyncSession, redis: Redis) -> AnalyticsService:
    return AnalyticsService(session, NotificationService(redis))


@router.get("/overview", response_model=OverviewMetrics)
async def overview(
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(redis_dependency),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ANALYST)),
) -> OverviewMetrics:
    return await analytics_service(session, redis).overview()


@router.get("/workflow-metrics", response_model=WorkflowMetrics)
async def workflow_metrics(
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(redis_dependency),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ANALYST)),
) -> WorkflowMetrics:
    return await analytics_service(session, redis).workflow_metrics()


@router.get("/agent-performance", response_model=list[AgentPerformance])
async def agent_performance(
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(redis_dependency),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.ANALYST)),
) -> list[AgentPerformance]:
    return await analytics_service(session, redis).agent_performance()
