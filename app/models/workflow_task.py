from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import TaskStatus


class WorkflowTask(Base):
    __tablename__ = "workflow_tasks"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    workflow_id: Mapped[UUID] = mapped_column(ForeignKey("workflows.id", ondelete="CASCADE"), index=True)
    assigned_agent: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.PENDING, index=True)
    execution_logs: Mapped[list[dict]] = mapped_column(JSON, default=list)
    input_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    output_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workflow = relationship("Workflow", back_populates="tasks")

