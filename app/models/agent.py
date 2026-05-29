from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import AgentStatus, AgentType


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    agent_name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    agent_type: Mapped[AgentType] = mapped_column(Enum(AgentType), index=True)
    status: Mapped[AgentStatus] = mapped_column(Enum(AgentStatus), default=AgentStatus.IDLE, index=True)
    capabilities: Mapped[list[str]] = mapped_column(JSON, default=list)
    last_active: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

