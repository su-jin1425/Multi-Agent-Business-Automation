import asyncio
from typing import Any

from app.agents.base import AgentContext
from app.agents.registry import agent_registry
from app.models.enums import AgentType, WorkflowStatus, WorkflowType
from app.workflows.state import WorkflowState


class LangGraphWorkflowOrchestrator:
    """Runs agent workflows with LangGraph when installed, and a compatible fallback otherwise."""

    def __init__(self) -> None:
        try:
            from langgraph.graph import END, StateGraph  # type: ignore
        except Exception:
            END = StateGraph = None
        self._state_graph = StateGraph
        self._end = END

    def route_agents(self, workflow_type: WorkflowType, payload: dict[str, Any]) -> list[AgentType]:
        if workflow_type == WorkflowType.FINANCE:
            return [AgentType.FINANCE, AgentType.ANALYTICS]
        if workflow_type == WorkflowType.ANALYTICS:
            return [AgentType.ANALYTICS]
        if workflow_type == WorkflowType.SUPPORT:
            return [AgentType.SUPPORT, AgentType.OPERATIONS]
        if workflow_type == WorkflowType.OPERATIONS:
            return [AgentType.OPERATIONS]
        requested = payload.get("agents")
        if isinstance(requested, list):
            return [AgentType(item) for item in requested if item in AgentType._value2member_map_]
        return [AgentType.FINANCE, AgentType.ANALYTICS, AgentType.SUPPORT, AgentType.OPERATIONS]

    async def execute(self, state: WorkflowState) -> WorkflowState:
        if self._state_graph:
            return await self._execute_langgraph(state)
        return await self._execute_fallback(state)

    async def _execute_fallback(self, state: WorkflowState) -> WorkflowState:
        workflow_type = state["workflow_type"]
        payload = state.get("input_payload", {})
        agents = state.get("next_agents") or self.route_agents(workflow_type, payload)
        context = AgentContext(
            workflow_id=state.get("workflow_id"),
            task=f"Execute {workflow_type.value} workflow",
            payload=payload,
            memory={"prior_results": state.get("agent_results", [])},
        )
        results = await asyncio.gather(*(agent_registry.get(agent_type).execute(context) for agent_type in agents))
        delegated = [agent_type for result in results for agent_type in result.delegated_to]
        second_pass = [
            agent_type
            for agent_type in delegated
            if agent_type not in agents and agent_type not in {AgentType.SUPERVISOR}
        ]
        if second_pass:
            followups = await asyncio.gather(
                *(agent_registry.get(agent_type).execute(context) for agent_type in second_pass)
            )
            results.extend(followups)
        state["agent_results"] = [result.model_dump(mode="json") for result in results]
        state["status"] = WorkflowStatus.COMPLETED
        state["next_agents"] = second_pass
        return state

    async def _execute_langgraph(self, state: WorkflowState) -> WorkflowState:
        graph = self._state_graph(WorkflowState)

        async def supervisor(current: WorkflowState) -> WorkflowState:
            current["next_agents"] = self.route_agents(current["workflow_type"], current.get("input_payload", {}))
            current["status"] = WorkflowStatus.RUNNING
            return current

        async def run_agents(current: WorkflowState) -> WorkflowState:
            return await self._execute_fallback(current)

        graph.add_node("supervisor", supervisor)
        graph.add_node("agents", run_agents)
        graph.set_entry_point("supervisor")
        graph.add_edge("supervisor", "agents")
        graph.add_edge("agents", self._end)
        compiled = graph.compile()
        return await compiled.ainvoke(state)


workflow_orchestrator = LangGraphWorkflowOrchestrator()
