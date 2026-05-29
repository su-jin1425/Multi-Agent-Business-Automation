from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import TicketStatus
from app.schemas.common import ORMModel


class TicketCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=120)
    issue: str = Field(min_length=5)


class TicketUpdate(BaseModel):
    status: TicketStatus | None = None
    assigned_agent: str | None = None
    response_draft: str | None = None


class TicketRead(ORMModel):
    id: UUID
    customer_name: str
    issue: str
    sentiment: str
    assigned_agent: str | None
    status: TicketStatus
    response_draft: str | None
    created_at: datetime
    updated_at: datetime

