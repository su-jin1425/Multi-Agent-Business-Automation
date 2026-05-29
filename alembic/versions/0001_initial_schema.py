"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-28
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


user_role = postgresql.ENUM("ADMIN", "MANAGER", "ANALYST", "SUPPORT_EXECUTIVE", name="userrole")
workflow_status = postgresql.ENUM(
    "PENDING", "RUNNING", "COMPLETED", "FAILED", "RETRYING", "PAUSED", name="workflowstatus"
)
workflow_type = postgresql.ENUM("FINANCE", "ANALYTICS", "SUPPORT", "OPERATIONS", "HYBRID", name="workflowtype")
task_status = postgresql.ENUM("PENDING", "RUNNING", "COMPLETED", "FAILED", "RETRYING", name="taskstatus")
agent_type = postgresql.ENUM("FINANCE", "ANALYTICS", "SUPPORT", "OPERATIONS", "SUPERVISOR", name="agenttype")
agent_status = postgresql.ENUM("ACTIVE", "IDLE", "BUSY", "OFFLINE", "DEGRADED", name="agentstatus")
ticket_status = postgresql.ENUM("OPEN", "IN_PROGRESS", "ESCALATED", "RESOLVED", "CLOSED", name="ticketstatus")


def upgrade() -> None:
    bind = op.get_bind()
    
    # Clear alembic version to force fresh migration

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role", "users", ["role"])

    op.create_table(
        "agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("agent_name", sa.String(length=120), nullable=False),
        sa.Column("agent_type", agent_type, nullable=False),
        sa.Column("status", agent_status, nullable=False),
        sa.Column("capabilities", sa.JSON(), nullable=False),
        sa.Column("last_active", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_agents_agent_name", "agents", ["agent_name"], unique=True)
    op.create_index("ix_agents_agent_type", "agents", ["agent_type"])
    op.create_index("ix_agents_status", "agents", ["status"])

    op.create_table(
        "workflows",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workflow_name", sa.String(length=160), nullable=False),
        sa.Column("workflow_type", workflow_type, nullable=False),
        sa.Column("status", workflow_status, nullable=False),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("input_payload", sa.JSON(), nullable=False),
        sa.Column("result_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_workflows_workflow_name", "workflows", ["workflow_name"])
    op.create_index("ix_workflows_workflow_type", "workflows", ["workflow_type"])
    op.create_index("ix_workflows_status", "workflows", ["status"])

    op.create_table(
        "workflow_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "workflow_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workflows.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("assigned_agent", sa.String(length=80), nullable=False),
        sa.Column("status", task_status, nullable=False),
        sa.Column("execution_logs", sa.JSON(), nullable=False),
        sa.Column("input_payload", sa.JSON(), nullable=False),
        sa.Column("output_payload", sa.JSON(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_workflow_tasks_workflow_id", "workflow_tasks", ["workflow_id"])
    op.create_index("ix_workflow_tasks_assigned_agent", "workflow_tasks", ["assigned_agent"])
    op.create_index("ix_workflow_tasks_status", "workflow_tasks", ["status"])

    op.create_table(
        "analytics_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("report_type", sa.String(length=100), nullable=False),
        sa.Column(
            "generated_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("report_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_analytics_reports_report_type", "analytics_reports", ["report_type"])

    op.create_table(
        "support_tickets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_name", sa.String(length=120), nullable=False),
        sa.Column("issue", sa.Text(), nullable=False),
        sa.Column("sentiment", sa.String(length=40), nullable=False),
        sa.Column("assigned_agent", sa.String(length=80), nullable=True),
        sa.Column("status", ticket_status, nullable=False),
        sa.Column("response_draft", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_support_tickets_sentiment", "support_tickets", ["sentiment"])
    op.create_index("ix_support_tickets_status", "support_tickets", ["status"])


def downgrade() -> None:
    op.drop_index("ix_support_tickets_status", table_name="support_tickets")
    op.drop_index("ix_support_tickets_sentiment", table_name="support_tickets")
    op.drop_table("support_tickets")
    op.drop_index("ix_analytics_reports_report_type", table_name="analytics_reports")
    op.drop_table("analytics_reports")
    op.drop_index("ix_workflow_tasks_status", table_name="workflow_tasks")
    op.drop_index("ix_workflow_tasks_assigned_agent", table_name="workflow_tasks")
    op.drop_index("ix_workflow_tasks_workflow_id", table_name="workflow_tasks")
    op.drop_table("workflow_tasks")
    op.drop_index("ix_workflows_status", table_name="workflows")
    op.drop_index("ix_workflows_workflow_type", table_name="workflows")
    op.drop_index("ix_workflows_workflow_name", table_name="workflows")
    op.drop_table("workflows")
    op.drop_index("ix_agents_status", table_name="agents")
    op.drop_index("ix_agents_agent_type", table_name="agents")
    op.drop_index("ix_agents_agent_name", table_name="agents")
    op.drop_table("agents")
    op.drop_index("ix_users_role", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    bind = op.get_bind()
    for enum in [ticket_status, agent_status, agent_type, task_status, workflow_type, workflow_status, user_role]:
        enum.drop(bind, checkfirst=True)
