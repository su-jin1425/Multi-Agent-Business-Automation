from typing import Any

from app.agents.registry import agent_registry


class CrewAIAdapter:
    """Optional CrewAI integration with a deterministic fallback for local development."""

    def __init__(self) -> None:
        try:
            from crewai import Agent, Crew, Task  # type: ignore
        except Exception:
            Agent = Crew = Task = None
        self._agent_cls = Agent
        self._crew_cls = Crew
        self._task_cls = Task

    def build_business_crew(self) -> Any:
        if not self._crew_cls:
            return {"mode": "fallback", "agents": [agent.name for agent in agent_registry.all()]}
        crew_agents = [
            self._agent_cls(role=agent.name, goal=", ".join(agent.capabilities), backstory="Business automation expert")
            for agent in agent_registry.all()
        ]
        return self._crew_cls(agents=crew_agents, tasks=[])


crew_adapter = CrewAIAdapter()

