from app.agents.base import AgentContext, AgentResult, BusinessAgent
from app.models.enums import AgentType


class OperationsAgent(BusinessAgent):
    agent_type = AgentType.OPERATIONS
    name = "Operations Agent"
    capabilities = ["workflow_optimization", "task_scheduling", "dependency_management", "queue_management"]

    async def execute(self, context: AgentContext) -> AgentResult:
        tasks = context.payload.get("tasks", [])
        priority = context.payload.get("priority", "normal")
        ordered_tasks = sorted(tasks, key=lambda item: item.get("priority", 5)) if isinstance(tasks, list) else []
        return AgentResult(
            agent_type=self.agent_type,
            summary=f"Optimized workflow schedule with {len(ordered_tasks)} tasks.",
            confidence=0.86,
            data={
                "priority": priority,
                "optimized_tasks": ordered_tasks,
                "routing_decision": "parallelize-independent-tasks",
            },
        )
