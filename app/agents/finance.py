from statistics import mean

from app.agents.base import AgentContext, AgentResult, BusinessAgent
from app.models.enums import AgentType


class FinanceAgent(BusinessAgent):
    agent_type = AgentType.FINANCE
    name = "Finance Agent"
    capabilities = ["expense_analysis", "invoice_summary", "budget_recommendation", "anomaly_detection"]

    async def execute(self, context: AgentContext) -> AgentResult:
        expenses = context.payload.get("expenses", [])
        amounts = [float(item.get("amount", 0)) for item in expenses if isinstance(item, dict)]
        total = sum(amounts)
        average = mean(amounts) if amounts else 0.0
        anomalies = [item for item in expenses if float(item.get("amount", 0)) > average * 2 and average > 0]
        delegated = [AgentType.ANALYTICS] if context.payload.get("include_forecast") else []
        return AgentResult(
            agent_type=self.agent_type,
            summary=f"Processed {len(expenses)} expenses totaling {total:.2f}.",
            confidence=0.88,
            data={
                "expense_count": len(expenses),
                "total_expense": total,
                "average_expense": average,
                "anomalies": anomalies,
                "recommendation": "Review anomalous expenses and rebalance discretionary budgets.",
            },
            delegated_to=delegated,
        )
