from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    environment: str
    version: str
    timestamp: datetime


class EventPayload(BaseModel):
    workflow_id: UUID | None = None
    event_type: str
    payload: dict
