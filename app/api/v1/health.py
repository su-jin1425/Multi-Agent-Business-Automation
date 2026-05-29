from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import redis_dependency
from app.core.config import settings
from app.db.session import get_db_session
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", environment=settings.environment, version="1.0.0", timestamp=datetime.now(UTC))


@router.get("/ready")
async def readiness(session: AsyncSession = Depends(get_db_session), redis: Redis = Depends(redis_dependency)) -> dict:
    await session.execute(text("SELECT 1"))
    await redis.ping()
    return {"status": "ready"}
