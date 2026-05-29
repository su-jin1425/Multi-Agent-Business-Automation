from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import AgentStatus, AgentType
from app.schemas.common import ORMModel


class AgentRead(ORMModel):
    id: UUID
    agent_name: str
    agent_type: AgentType
    status: AgentStatus
    capabilities: list[str]
    last_active: datetime | None


class AgentExecuteRequest(BaseModel):
    agent_type: AgentType
    task: str = Field(min_length=3)
    context: dict = Field(default_factory=dict)


class AgentExecuteResponse(BaseModel):
    agent_type: AgentType
    result: dict
    delegated_to: list[str] = Field(default_factory=list)

