from app.agents.base import AgentContext, AgentResult, BusinessAgent
from app.models.enums import AgentType


NEGATIVE_TERMS = {"angry", "bad", "broken", "cancel", "complaint", "failed", "late", "refund", "terrible"}


class SupportAgent(BusinessAgent):
    agent_type = AgentType.SUPPORT
    name = "Support Agent"
    capabilities = ["ticket_triage", "response_generation", "escalation", "sentiment_detection"]

    async def execute(self, context: AgentContext) -> AgentResult:
        issue = str(context.payload.get("issue", context.task))
        lowered = issue.lower()
        negative_hits = [term for term in NEGATIVE_TERMS if term in lowered]
        sentiment = "negative" if negative_hits else "neutral"
        needs_escalation = any(term in lowered for term in {"legal", "security", "breach", "vip", "refund"})
        response = (
            "Thanks for reaching out. We have triaged the issue and routed it to the right team."
            if not needs_escalation
            else "Thanks for the details. This needs specialist review and has been escalated."
        )
        return AgentResult(
            agent_type=self.agent_type,
            summary="Support ticket classified and response drafted.",
            confidence=0.81,
            data={"sentiment": sentiment, "escalate": needs_escalation, "response_draft": response},
            delegated_to=[AgentType.OPERATIONS] if needs_escalation else [],
        )

