from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.models.enums import AgentStatus, TaskStatus, TicketStatus, WorkflowStatus
from app.models.support_ticket import SupportTicket
from app.models.workflow import Workflow
from app.models.workflow_task import WorkflowTask
from app.schemas.analytics import AgentPerformance, OverviewMetrics, WorkflowMetrics
from app.services.notification_service import NotificationService


class AnalyticsService:
    def __init__(self, session: AsyncSession, notification_service: NotificationService) -> None:
        self.session = session
        self.notifications = notification_service

    async def overview(self) -> OverviewMetrics:
        workflows = (await self.session.execute(select(Workflow))).scalars().all()
        agents = (await self.session.execute(select(Agent))).scalars().all()
        tickets = (await self.session.execute(select(SupportTicket))).scalars().all()
        return OverviewMetrics(
            workflows_total=len(workflows),
            workflows_completed=sum(1 for item in workflows if item.status == WorkflowStatus.COMPLETED),
            workflows_failed=sum(1 for item in workflows if item.status == WorkflowStatus.FAILED),
            active_agents=sum(1 for item in agents if item.status in {AgentStatus.ACTIVE, AgentStatus.BUSY}),
            open_tickets=sum(1 for item in tickets if item.status in {TicketStatus.OPEN, TicketStatus.IN_PROGRESS}),
            queue_size=await self.notifications.queue_size(),
        )

    async def workflow_metrics(self) -> WorkflowMetrics:
        workflows = (await self.session.execute(select(Workflow))).scalars().all()
        by_status = {status.value: sum(1 for item in workflows if item.status == status) for status in WorkflowStatus}
        total = len(workflows) or 1
        completed = by_status[WorkflowStatus.COMPLETED.value]
        failed = by_status[WorkflowStatus.FAILED.value]
        return WorkflowMetrics(by_status=by_status, completion_rate=completed / total, failure_rate=failed / total)

    async def agent_performance(self) -> list[AgentPerformance]:
        agents = (await self.session.execute(select(Agent))).scalars().all()
        tasks = (await self.session.execute(select(WorkflowTask))).scalars().all()
        rows: list[AgentPerformance] = []
        for agent in agents:
            agent_tasks = [task for task in tasks if task.assigned_agent == agent.agent_type.value]
            completed = [task for task in agent_tasks if task.status == TaskStatus.COMPLETED]
            failed = [task for task in agent_tasks if task.status == TaskStatus.FAILED]
            latencies = [
                (task.completed_at - task.started_at).total_seconds() * 1000
                for task in completed
                if task.completed_at and task.started_at
            ]
            rows.append(
                AgentPerformance(
                    agent_name=agent.agent_name,
                    agent_type=agent.agent_type.value,
                    completed_tasks=len(completed),
                    failed_tasks=len(failed),
                    average_latency_ms=sum(latencies) / len(latencies) if latencies else 0.0,
                )
            )
        return rows

