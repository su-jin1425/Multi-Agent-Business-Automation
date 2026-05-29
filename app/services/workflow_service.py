import time
from datetime import UTC, datetime
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError, NotFoundError
from app.models.enums import TaskStatus, WorkflowStatus
from app.models.workflow import Workflow
from app.monitoring.metrics import task_latency, workflow_counter
from app.repositories.workflows import WorkflowRepository, WorkflowTaskRepository
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate
from app.services.notification_service import NotificationService
from app.workflows.langgraph_orchestrator import workflow_orchestrator


class WorkflowService:
    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self.session = session
        self.redis = redis
        self.workflows = WorkflowRepository(session)
        self.tasks = WorkflowTaskRepository(session)
        self.notifications = NotificationService(redis)

    async def create(self, payload: WorkflowCreate, created_by: UUID | None) -> Workflow:
        workflow = await self.workflows.create(
            workflow_name=payload.workflow_name,
            workflow_type=payload.workflow_type,
            input_payload=payload.input_payload,
            created_by=created_by,
        )
        await self.session.commit()
        await self.notifications.publish_workflow_event(workflow.id, "workflow.created", {"status": workflow.status})
        return await self.get(workflow.id)

    async def list(self) -> list[Workflow]:
        return list(await self.workflows.list_with_tasks())

    async def get(self, workflow_id: UUID) -> Workflow:
        workflow = await self.workflows.get_with_tasks(workflow_id)
        if not workflow:
            raise NotFoundError("Workflow")
        return workflow

    async def update(self, workflow_id: UUID, payload: WorkflowUpdate) -> Workflow:
        workflow = await self.get(workflow_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(workflow, key, value)
        await self.session.commit()
        await self.notifications.publish_workflow_event(workflow.id, "workflow.updated", {"status": workflow.status})
        return await self.get(workflow_id)

    async def delete(self, workflow_id: UUID) -> None:
        workflow = await self.get(workflow_id)
        await self.workflows.delete(workflow)
        await self.session.commit()
        await self.notifications.publish_workflow_event(workflow_id, "workflow.deleted", {})

    async def pause(self, workflow_id: UUID) -> Workflow:
        workflow = await self.get(workflow_id)
        if workflow.status not in {WorkflowStatus.PENDING, WorkflowStatus.RUNNING, WorkflowStatus.RETRYING}:
            raise AppError("Only pending, running, or retrying workflows can be paused")
        workflow.status = WorkflowStatus.PAUSED
        await self.session.commit()
        await self.notifications.publish_workflow_event(workflow.id, "workflow.paused", {})
        return await self.get(workflow_id)

    async def resume(self, workflow_id: UUID) -> Workflow:
        workflow = await self.get(workflow_id)
        if workflow.status != WorkflowStatus.PAUSED:
            raise AppError("Only paused workflows can be resumed")
        workflow.status = WorkflowStatus.PENDING
        await self.session.commit()
        await self.notifications.publish_workflow_event(workflow.id, "workflow.resumed", {})
        return await self.get(workflow_id)

    async def execute(self, workflow_id: UUID) -> Workflow:
        workflow = await self.get(workflow_id)
        if workflow.status == WorkflowStatus.PAUSED:
            raise AppError("Paused workflows cannot be executed")
        workflow.status = WorkflowStatus.RUNNING
        await self.session.commit()
        await self.notifications.publish_workflow_event(workflow.id, "workflow.running", {})

        started = time.perf_counter()
        routed_agents = workflow_orchestrator.route_agents(workflow.workflow_type, workflow.input_payload)
        created_tasks = []
        for agent_type in routed_agents:
            created_tasks.append(
                await self.tasks.create(
                    workflow_id=workflow.id,
                    assigned_agent=agent_type.value,
                    status=TaskStatus.RUNNING,
                    input_payload=workflow.input_payload,
                    started_at=datetime.now(UTC),
                    execution_logs=[{"event": "task.started", "agent": agent_type.value}],
                )
            )
        await self.session.flush()

        try:
            state = await workflow_orchestrator.execute(
                {
                    "workflow_id": str(workflow.id),
                    "workflow_type": workflow.workflow_type,
                    "status": workflow.status,
                    "input_payload": workflow.input_payload,
                    "agent_results": [],
                }
            )
            workflow.status = WorkflowStatus.COMPLETED
            workflow.result_payload = {"agent_results": state.get("agent_results", [])}
            for task, result in zip(created_tasks, state.get("agent_results", []), strict=False):
                task.status = TaskStatus.COMPLETED
                task.output_payload = result
                task.completed_at = datetime.now(UTC)
                task.execution_logs = [*task.execution_logs, {"event": "task.completed", "agent": task.assigned_agent}]
                task_latency.labels(agent_type=task.assigned_agent).observe(time.perf_counter() - started)
            workflow_counter.labels(status=workflow.status.value, workflow_type=workflow.workflow_type.value).inc()
        except Exception as exc:
            workflow.status = WorkflowStatus.FAILED
            workflow.result_payload = {"error": str(exc)}
            for task in created_tasks:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now(UTC)
                task.execution_logs = [*task.execution_logs, {"event": "task.failed", "error": str(exc)}]
            workflow_counter.labels(status=workflow.status.value, workflow_type=workflow.workflow_type.value).inc()
            await self.session.commit()
            await self.notifications.publish_workflow_event(workflow.id, "workflow.failed", {"error": str(exc)})
            raise

        await self.session.commit()
        await self.notifications.cache_workflow_state(workflow.id, workflow.result_payload)
        await self.notifications.publish_workflow_event(workflow.id, "workflow.completed", workflow.result_payload)
        return await self.get(workflow.id)

    async def retry(self, workflow_id: UUID) -> Workflow:
        workflow = await self.get(workflow_id)
        workflow.status = WorkflowStatus.RETRYING
        await self.session.commit()
        await self.notifications.publish_workflow_event(workflow.id, "workflow.retrying", {})
        return await self.execute(workflow_id)
