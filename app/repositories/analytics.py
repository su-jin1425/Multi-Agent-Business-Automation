from app.models.analytics_report import AnalyticsReport
from app.repositories.base import BaseRepository


class AnalyticsReportRepository(BaseRepository[AnalyticsReport]):
    model = AnalyticsReport
