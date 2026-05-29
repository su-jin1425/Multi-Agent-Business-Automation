from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import AgentType


class AgentContext(BaseModel):
    workflow_id: str | None = None
    task: str
    payload: dict[str, Any] = Field(default_factory=dict)
    memory: dict[str, Any] = Field(default_factory=dict)


class AgentResult(BaseModel):
    agent_type: AgentType
    summary: str
    confidence: float = Field(ge=0, le=1)
    data: dict[str, Any] = Field(default_factory=dict)
    delegated_to: list[AgentType] = Field(default_factory=list)
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class BusinessAgent(ABC):
    agent_type: AgentType
    name: str
    capabilities: list[str]

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute an autonomous business task."""

