import asyncio
from uuid import UUID

from celery import Celery

from app.core.config import settings
from app.db.redis import redis_client
from app.db.session import AsyncSessionLocal
from app.services.workflow_service import WorkflowService


celery_app = Celery(
    "business_automation",
    broker=settings.broker_url,
    backend=settings.result_backend_url,
    include=["app.tasks"],
)
celery_app.conf.task_routes = {"app.tasks.execute_workflow_task": {"queue": "workflows"}}
celery_app.conf.task_acks_late = True
celery_app.conf.worker_prefetch_multiplier = 1


@celery_app.task(
    name="app.tasks.execute_workflow_task",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def execute_workflow_task(self, workflow_id: str) -> dict:  # type: ignore[no-untyped-def]
    async def runner() -> dict:
        async with AsyncSessionLocal() as session:
            workflow = await WorkflowService(session, redis_client).execute(UUID(workflow_id))
            return {"workflow_id": str(workflow.id), "status": workflow.status.value}

    return asyncio.run(runner())
