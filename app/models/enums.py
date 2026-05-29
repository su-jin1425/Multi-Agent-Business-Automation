from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    SUPPORT_EXECUTIVE = "support_executive"


class WorkflowStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    PAUSED = "paused"


class WorkflowType(StrEnum):
    FINANCE = "finance"
    ANALYTICS = "analytics"
    SUPPORT = "support"
    OPERATIONS = "operations"
    HYBRID = "hybrid"


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class AgentType(StrEnum):
    FINANCE = "finance"
    ANALYTICS = "analytics"
    SUPPORT = "support"
    OPERATIONS = "operations"
    SUPERVISOR = "supervisor"


class AgentStatus(StrEnum):
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    DEGRADED = "degraded"


class TicketStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"

