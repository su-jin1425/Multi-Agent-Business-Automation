from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import TaskStatus, WorkflowStatus, WorkflowType
from app.schemas.common import ORMModel


class WorkflowTaskRead(ORMModel):
    id: UUID
    workflow_id: UUID
    assigned_agent: str
    status: TaskStatus
    execution_logs: list[dict]
    input_payload: dict
    output_payload: dict
    started_at: datetime | None
    completed_at: datetime | None


class WorkflowCreate(BaseModel):
    workflow_name: str = Field(min_length=3, max_length=160)
    workflow_type: WorkflowType
    input_payload: dict = Field(default_factory=dict)


class WorkflowUpdate(BaseModel):
    workflow_name: str | None = Field(default=None, min_length=3, max_length=160)
    status: WorkflowStatus | None = None
    input_payload: dict | None = None


class WorkflowRead(ORMModel):
    id: UUID
    workflow_name: str
    workflow_type: WorkflowType
    status: WorkflowStatus
    created_by: UUID | None
    input_payload: dict
    result_payload: dict
    created_at: datetime
    updated_at: datetime
    tasks: list[WorkflowTaskRead] = []


class WorkflowTriggerResponse(BaseModel):
    workflow_id: UUID
    status: WorkflowStatus
    celery_task_id: str | None = None
    message: str
