from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.enums import WorkflowStatus
from app.models.workflow import Workflow
from app.models.workflow_task import WorkflowTask
from app.repositories.base import BaseRepository


class WorkflowRepository(BaseRepository[Workflow]):
    model = Workflow

    async def get_with_tasks(self, workflow_id: UUID) -> Workflow | None:
        result = await self.session.execute(
            select(Workflow).options(selectinload(Workflow.tasks)).where(Workflow.id == workflow_id)
        )
        return result.scalar_one_or_none()

    async def list_with_tasks(self, *, limit: int = 100, offset: int = 0) -> Sequence[Workflow]:
        result = await self.session.execute(
            select(Workflow)
            .options(selectinload(Workflow.tasks))
            .order_by(Workflow.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def count_by_status(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for status in WorkflowStatus:
            rows = await self.session.execute(select(Workflow).where(Workflow.status == status))
            result[status.value] = len(rows.scalars().all())
        return result


class WorkflowTaskRepository(BaseRepository[WorkflowTask]):
    model = WorkflowTask

    async def list_for_workflow(self, workflow_id: UUID) -> Sequence[WorkflowTask]:
        result = await self.session.execute(
            select(WorkflowTask).where(WorkflowTask.workflow_id == workflow_id).order_by(WorkflowTask.started_at)
        )
        return result.scalars().all()
