from app.agents.base import AgentContext, AgentResult, BusinessAgent
from app.models.enums import AgentType


class OperationsAgent(BusinessAgent):
    agent_type = AgentType.OPERATIONS
    name = "Operations Agent"
    capabilities = [
        "workflow_optimization",
        "task_scheduling",
        "dependency_management",
        "queue_management",
    ]

    async def execute(self, context: AgentContext) -> AgentResult:
        tasks = context.payload.get("tasks", [])
        priority = context.payload.get("priority", "normal")

        normalized_tasks = []

        for task in tasks:
            # Handle string tasks
            if isinstance(task, str):
                normalized_tasks.append(
                    {
                        "name": task,
                        "priority": "normal",
                    }
                )

            # Handle dictionary tasks
            elif isinstance(task, dict):
                normalized_tasks.append(
                    {
                        "name": task.get("name", "Unnamed Task"),
                        "priority": task.get("priority", "normal"),
                    }
                )

        priority_order = {
            "high": 1,
            "medium": 2,
            "normal": 3,
            "low": 4,
        }

        ordered_tasks = sorted(
            normalized_tasks,
            key=lambda item: priority_order.get(
                item.get("priority", "normal"),
                3,
            ),
        )

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