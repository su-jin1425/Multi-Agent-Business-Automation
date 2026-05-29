from app.agents.base import AgentContext, AgentResult, BusinessAgent
from app.models.enums import AgentType


class AnalyticsAgent(BusinessAgent):
    agent_type = AgentType.ANALYTICS
    name = "Analytics Agent"
    capabilities = ["kpi_generation", "trend_analysis", "predictive_summary", "visualization_preparation"]

    async def execute(self, context: AgentContext) -> AgentResult:
        metrics = context.payload.get("metrics", {})
        numeric_values = [float(value) for value in metrics.values() if isinstance(value, int | float)]
        trend = "stable"
        if len(numeric_values) >= 2 and numeric_values[-1] > numeric_values[0]:
            trend = "upward"
        elif len(numeric_values) >= 2 and numeric_values[-1] < numeric_values[0]:
            trend = "downward"
        return AgentResult(
            agent_type=self.agent_type,
            summary=f"Generated KPI snapshot with {trend} trend.",
            confidence=0.84,
            data={
                "kpis": metrics,
                "trend": trend,
                "forecast_summary": "Forecast based on current payload indicates moderate operational variance.",
                "chart_spec": {"type": "line", "series": list(metrics.items())},
            },
        )
