from pydantic import BaseModel


class OverviewMetrics(BaseModel):
    workflows_total: int
    workflows_completed: int
    workflows_failed: int
    active_agents: int
    open_tickets: int
    queue_size: int


class WorkflowMetrics(BaseModel):
    by_status: dict[str, int]
    completion_rate: float
    failure_rate: float


class AgentPerformance(BaseModel):
    agent_name: str
    agent_type: str
    completed_tasks: int
    failed_tasks: int
    average_latency_ms: float
