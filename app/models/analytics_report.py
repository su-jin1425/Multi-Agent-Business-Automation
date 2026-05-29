from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AnalyticsReport(Base):
    __tablename__ = "analytics_reports"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    report_type: Mapped[str] = mapped_column(String(100), index=True)
    generated_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    report_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
