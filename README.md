# Multi-Agent Business Automation System

Production-oriented backend platform for finance, analytics, operations, and customer support automation using autonomous agents coordinated through a unified API gateway.

---

## Table of Contents

- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Environment Configuration](#environment-configuration)
- [Database Migration](#database-migration)
- [API Reference](#api-reference)
  - [Health and Readiness](#health-and-readiness)
  - [Authentication](#authentication)
  - [Workflows](#workflows)
  - [Agents](#agents)
  - [Analytics](#analytics)
  - [Support Tickets](#support-tickets)
  - [Prometheus Metrics](#prometheus-metrics)
- [Database Verification](#database-verification)
- [Workflow Lifecycle](#workflow-lifecycle)
- [Agent Assignment Map](#agent-assignment-map)

---

## Architecture

```mermaid
graph TB
    Client["Clients / Dashboards"]
    GW["FastAPI API Gateway<br/>JWT | RBAC | Rate Limit"]
    Auth["Auth Service<br/>Login | Register | Token"]
    WF["Workflow Service<br/>CRUD | Trigger | Execute"]
    WFO["Workflow Orchestrator<br/>LangGraph State Machine"]
    AgentSvc["Agent Service<br/>Finance | Analytics | Support | Operations"]
    Agents["Agent Framework<br/>CrewAI | AutoGen | LangGraph"]
    DB[("PostgreSQL<br/>Users | Workflows | Tickets")]
    Cache[("Redis Cache<br/>Session | Rate Limit | Pub/Sub")]
    Queue["Celery Queue<br/>Distributed Tasks"]
    Monitor["Prometheus<br/>Metrics & Monitoring"]
    Grafana["Grafana Dashboard<br/>Visualization & Alerts"]

    Client --> GW
    GW --> Auth
    GW --> WF
    GW --> AgentSvc
    WF --> WFO
    WFO --> Agents
    AgentSvc --> Agents
    WF --> DB
    WF --> Queue
    Queue --> Agents
    Agents --> DB
    Auth --> DB
    GW --> Cache
    Agents --> Cache
    GW --> Monitor
    Monitor --> Grafana
```

---

## Tech Stack

| Layer         | Technology                             |
|---------------|----------------------------------------|
| API Gateway   | FastAPI, JWT, RBAC, Rate Limiting      |
| Orchestration | LangGraph State Machine                |
| Agents        | CrewAI, AutoGen, LangGraph             |
| Database      | PostgreSQL                             |
| Cache         | Redis                                  |
| Task Queue    | Celery                                 |
| Monitoring    | Prometheus, Grafana                    |
| Containers    | Docker, Docker Compose                 |

---

## Prerequisites

- Docker Desktop (latest stable)
- Docker Compose v2+
- PowerShell 5.1+ or PowerShell Core 7+ (Windows) or any shell with curl (Linux/macOS)
- PostgreSQL client (optional, for direct DB inspection)

---

## Quick Start

### 1. Clone and Configure

```powershell
cp .env.example .env
```

Edit `.env` with your credentials before proceeding.

### 2. Build and Start All Services

```powershell
docker-compose up --build
```

This starts the API server, PostgreSQL, Redis, Celery workers, Prometheus, and Grafana.

### 3. Apply Database Migrations

```powershell
docker-compose exec backend alembic upgrade head
```

### 4. Verify the Stack is Healthy

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health"
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/ready"
```

---

## Environment Configuration

Copy `.env.example` to `.env` and update the following values:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/automation_db

# Redis
REDIS_URL=redis://localhost:6379

# JWT
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# LLM Provider (if applicable)
OPENAI_API_KEY=your-api-key
```

---

## Database Migration

```powershell
# Run all pending migrations
docker-compose exec backend alembic upgrade head

# Connect to PostgreSQL directly
docker exec -it automation-postgres psql -U postgres -d automation_db
```

---

## API Reference

All protected endpoints require a Bearer token in the `Authorization` header.

Base URL: `http://localhost:8000/api/v1`

---

### Health and Readiness

#### List All Endpoints

```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/openapi.json"

$response.paths.PSObject.Properties | ForEach-Object {
    [PSCustomObject]@{
        Path    = $_.Name
        Methods = ($_.Value.PSObject.Properties.Name -join ", ").ToUpper()
    }
} | Sort-Object Path | Format-Table -AutoSize

Write-Host ""
Write-Host "Total Endpoints:" (($response.paths.PSObject.Properties.Name).Count)
```

#### Health Check

```
GET /api/v1/health
```

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health"
```

#### Readiness Check

```
GET /api/v1/ready
```

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/ready"
```

---

### Authentication

#### Register a New User

```
POST /api/v1/auth/register
```

Available roles: `admin`, `manager`, `analyst`, `support_executive`

```powershell
$registerBody = @{
    name     = "User"
    email    = "user@example.com"
    password = "Password123!"
    role     = "admin"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/auth/register" `
    -Method Post `
    -ContentType "application/json" `
    -Body $registerBody
```

#### Login

```
POST /api/v1/auth/login
```

```powershell
$loginBody = @{
    email    = "user@example.com"
    password = "Password123!"
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method Post `
    -ContentType "application/json" `
    -Body $loginBody

$token = $response.access_token
$token
```

> Store `$token` — it is required for all subsequent requests.

#### Verify Current Session

```
GET /api/v1/auth/me
```

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/auth/me" `
    -Headers @{ Authorization = "Bearer $token" }
```

---

### Workflows

#### List All Workflows

```
GET /api/v1/workflows
```

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows" `
    -Method Get `
    -Headers @{ Authorization = "Bearer $token" }
```

---

#### Create Workflow

```
POST /api/v1/workflows
```

**Finance**

```powershell
$body = @{
    workflow_name = "Monthly Expense Analysis"
    workflow_type = "finance"
    input_payload = @{
        expenses = @(
            @{ department = "Engineering"; amount = 50000 }
            @{ department = "Marketing";   amount = 25000 }
            @{ department = "Operations";  amount = 15000 }
        )
    }
} | ConvertTo-Json -Depth 10

$financeWorkflow   = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows" `
    -Method Post `
    -Headers @{ Authorization = "Bearer $token" } `
    -ContentType "application/json" `
    -Body $body

$financeWorkflowId = $financeWorkflow.id
$financeWorkflowId
```

**Analytics**

```powershell
$body = @{
    workflow_name = "Analytics Test"
    workflow_type = "analytics"
    input_payload = @{
        sales = @(120000, 135000, 142000)
    }
} | ConvertTo-Json -Depth 10

$analyticsWorkflow   = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows" `
    -Method Post `
    -Headers @{ Authorization = "Bearer $token" } `
    -ContentType "application/json" `
    -Body $body

$analyticsWorkflowId = $analyticsWorkflow.id
$analyticsWorkflowId
```

**Support**

```powershell
$body = @{
    workflow_name = "Support Test"
    workflow_type = "support"
    input_payload = @{
        issue = "Unable to login after password reset"
    }
} | ConvertTo-Json -Depth 10

$supportWorkflow   = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows" `
    -Method Post `
    -Headers @{ Authorization = "Bearer $token" } `
    -ContentType "application/json" `
    -Body $body

$supportWorkflowId = $supportWorkflow.id
$supportWorkflowId
```

**Operations**

```powershell
$body = @{
    workflow_name = "Operations Test"
    workflow_type = "operations"
    input_payload = @{
        tasks = @("Generate Report", "Send Email", "Create Dashboard")
    }
} | ConvertTo-Json -Depth 10

$operationsWorkflow   = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows" `
    -Method Post `
    -Headers @{ Authorization = "Bearer $token" } `
    -ContentType "application/json" `
    -Body $body

$operationsWorkflowId = $operationsWorkflow.id
$operationsWorkflowId
```

---

#### Get a Workflow

```
GET /api/v1/workflows/{workflow_id}
```

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$financeWorkflowId"   -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$analyticsWorkflowId" -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$supportWorkflowId"   -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$operationsWorkflowId"-Headers @{ Authorization = "Bearer $token" }
```

---

#### Update a Workflow

```
PUT /api/v1/workflows/{workflow_id}
```

```powershell
$body = @{
    workflow_name = "Updated Expense Analysis"
    workflow_type = "finance"
    input_payload = @{
        expenses = @(
            @{ department = "Engineering"; amount = 75000 }
            @{ department = "Marketing";   amount = 35000 }
        )
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows/$financeWorkflowId" `
    -Method Put `
    -Headers @{ Authorization = "Bearer $token" } `
    -ContentType "application/json" `
    -Body $body
```

---

#### Delete a Workflow

```
DELETE /api/v1/workflows/{workflow_id}
```

Create a duplicate to safely test deletion:

```powershell
$body = @{
    workflow_name = "Monthly Expense Analysis"
    workflow_type = "finance"
    input_payload = @{
        expenses = @(
            @{ department = "Engineering"; amount = 50000 }
            @{ department = "Marketing";   amount = 25000 }
            @{ department = "Operations";  amount = 15000 }
        )
    }
} | ConvertTo-Json -Depth 10

$financeWorkflow     = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows" `
    -Method Post `
    -Headers @{ Authorization = "Bearer $token" } `
    -ContentType "application/json" `
    -Body $body

$duplicateWorkflowId = $financeWorkflow.id
$duplicateWorkflowId
```

Delete it:

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows/$duplicateWorkflowId" `
    -Method Delete `
    -Headers @{ Authorization = "Bearer $token" }
```

---

#### Trigger a Workflow (Async)

```
POST /api/v1/workflows/{workflow_id}/trigger
```

Queues the workflow as a Celery job and returns immediately. Status transitions: `PENDING -> RUNNING -> COMPLETED` or `FAILED`.

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$financeWorkflowId/trigger"    -Method Post -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$analyticsWorkflowId/trigger"  -Method Post -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$supportWorkflowId/trigger"    -Method Post -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$operationsWorkflowId/trigger" -Method Post -Headers @{ Authorization = "Bearer $token" }
```

---

#### Execute a Workflow (Synchronous)

```
POST /api/v1/workflows/{workflow_id}/execute
```

Runs the workflow inline and blocks until a result is returned.

| Mode      | Behavior                                   |
|-----------|--------------------------------------------|
| `/trigger` | Enqueues in Celery, returns immediately   |
| `/execute` | Runs now, waits for result, returns result |

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$financeWorkflowId/execute"    -Method Post -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$analyticsWorkflowId/execute"  -Method Post -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$supportWorkflowId/execute"    -Method Post -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$operationsWorkflowId/execute" -Method Post -Headers @{ Authorization = "Bearer $token" }
```

Fetch the result immediately after execution:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$analyticsWorkflowId" -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$supportWorkflowId"   -Headers @{ Authorization = "Bearer $token" }
```

---

#### Pause a Workflow

```
POST /api/v1/workflows/{workflow_id}/pause
```

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$financeWorkflowId/pause"    -Method Post -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$analyticsWorkflowId/pause"  -Method Post -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$supportWorkflowId/pause"    -Method Post -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$operationsWorkflowId/pause" -Method Post -Headers @{ Authorization = "Bearer $token" }
```

Verify pause state:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$operationsWorkflowId" -Headers @{ Authorization = "Bearer $token" }
```

---

#### Resume a Workflow

```
POST /api/v1/workflows/{workflow_id}/resume
```

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$financeWorkflowId/resume"    -Method Post -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$analyticsWorkflowId/resume"  -Method Post -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$supportWorkflowId/resume"    -Method Post -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$operationsWorkflowId/resume" -Method Post -Headers @{ Authorization = "Bearer $token" }
```

Verify resume state:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$operationsWorkflowId" -Headers @{ Authorization = "Bearer $token" }
```

---

#### Retry a Workflow

```
POST /api/v1/workflows/{workflow_id}/retry
```

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$financeWorkflowId/retry"    -Method Post -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$analyticsWorkflowId/retry"  -Method Post -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$supportWorkflowId/retry"    -Method Post -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/workflows/$operationsWorkflowId/retry" -Method Post -Headers @{ Authorization = "Bearer $token" }
```

Print the workflow ID for PostgreSQL lookup:

```powershell
Write-Host $operationsWorkflowId
```

---

### Agents

#### List All Agents

```
GET /api/v1/agents
```

```powershell
$agents = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/agents" `
    -Headers @{ Authorization = "Bearer $token" }

$financeAgentId    = ($agents | Where-Object { $_.agent_type -eq "finance" }).id
$supportAgentId    = ($agents | Where-Object { $_.agent_type -eq "support" }).id
$operationsAgentId = ($agents | Where-Object { $_.agent_type -eq "operations" }).id
$analyticsAgentId  = ($agents | Where-Object { $_.agent_type -eq "analytics" }).id

Write-Host "Finance Agent ID:    $financeAgentId"
Write-Host "Support Agent ID:    $supportAgentId"
Write-Host "Operations Agent ID: $operationsAgentId"
Write-Host "Analytics Agent ID:  $analyticsAgentId"
```

---

#### Get a Specific Agent

```
GET /api/v1/agents/{agent_id}
```

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/agents/$financeAgentId"    -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/agents/$supportAgentId"    -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/agents/$operationsAgentId" -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/agents/$analyticsAgentId"  -Headers @{ Authorization = "Bearer $token" }
```

---

#### Execute an Agent Directly

```
POST /api/v1/agents/execute
```

**Finance Agent**

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/agents/execute" `
    -Method Post `
    -Headers @{ Authorization = "Bearer $token" } `
    -ContentType "application/json" `
    -Body (@{
        agent_type = "finance"
        task       = "Analyze monthly department expenses"
        context    = @{
            expenses = @(
                @{ department = "Engineering"; amount = 50000 }
                @{ department = "Marketing";   amount = 25000 }
                @{ department = "Operations";  amount = 15000 }
            )
        }
    } | ConvertTo-Json -Depth 10)
```

**Analytics Agent**

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/agents/execute" `
    -Method Post `
    -Headers @{ Authorization = "Bearer $token" } `
    -ContentType "application/json" `
    -Body (@{
        agent_type = "analytics"
        task       = "Analyze sales trends"
        context    = @{
            sales = @(120000, 135000, 142000)
        }
    } | ConvertTo-Json -Depth 10)
```

**Support Agent**

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/agents/execute" `
    -Method Post `
    -Headers @{ Authorization = "Bearer $token" } `
    -ContentType "application/json" `
    -Body (@{
        agent_type = "support"
        task       = "Handle customer login issue"
        context    = @{
            issue = "Unable to login after password reset"
        }
    } | ConvertTo-Json -Depth 10)
```

**Operations Agent — String Tasks**

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/agents/execute" `
    -Method Post `
    -Headers @{ Authorization = "Bearer $token" } `
    -ContentType "application/json" `
    -Body (@{
        agent_type = "operations"
        task       = "Optimize workflow schedule"
        context    = @{
            tasks = @("Generate Report", "Send Email", "Create Dashboard")
        }
    } | ConvertTo-Json -Depth 10)
```

**Operations Agent — Priority Tasks**

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/agents/execute" `
    -Method Post `
    -Headers @{ Authorization = "Bearer $token" } `
    -ContentType "application/json" `
    -Body (@{
        agent_type = "operations"
        task       = "Optimize workflow schedule"
        context    = @{
            tasks = @(
                @{ name = "Generate Report";    priority = "high" }
                @{ name = "Send Email";         priority = "medium" }
                @{ name = "Create Dashboard";   priority = "low" }
            )
        }
    } | ConvertTo-Json -Depth 10)
```

---

### Analytics

#### Analytics Overview

```
GET /api/v1/analytics/overview
```

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/analytics/overview" `
    -Headers @{ Authorization = "Bearer $token" } `
    | ConvertTo-Json -Depth 10
```

#### Workflow Metrics

```
GET /api/v1/analytics/workflow-metrics
```

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/analytics/workflow-metrics" `
    -Headers @{ Authorization = "Bearer $token" } `
    | ConvertTo-Json -Depth 10
```

#### Agent Performance

```
GET /api/v1/analytics/agent-performance
```

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/analytics/agent-performance" `
    -Headers @{ Authorization = "Bearer $token" } `
    | ConvertTo-Json -Depth 10
```

---

### Support Tickets

#### List All Tickets

```
GET /api/v1/tickets
```

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/tickets" `
    -Headers @{ Authorization = "Bearer $token" } `
    | Format-Table -AutoSize
```

---

#### Create a Ticket

```
POST /api/v1/tickets
```

**Ticket 1 — Login Issue**

```powershell
$body = @{
    customer_name  = "John Smith"
    customer_email = "john.smith@example.com"
    issue          = "Unable to login after password reset"
} | ConvertTo-Json

$ticket1   = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/tickets" `
    -Method Post `
    -Headers @{ Authorization = "Bearer $token" } `
    -ContentType "application/json" `
    -Body $body

$ticket1Id = $ticket1.id
Write-Host "Ticket 1 ID: $ticket1Id"
```

**Ticket 2 — Payment Issue**

```powershell
$body = @{
    customer_name  = "Sarah Johnson"
    customer_email = "sarah.johnson@example.com"
    issue          = "Payment was deducted twice but the order was not created"
} | ConvertTo-Json

$ticket2   = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/tickets" `
    -Method Post `
    -Headers @{ Authorization = "Bearer $token" } `
    -ContentType "application/json" `
    -Body $body

$ticket2Id = $ticket2.id
Write-Host "Ticket 2 ID: $ticket2Id"
```

**Ticket 3 — Dashboard Issue**

```powershell
$body = @{
    customer_name  = "Michael Brown"
    customer_email = "michael.brown@example.com"
    issue          = "Unable to access the analytics dashboard after the recent update"
} | ConvertTo-Json

$ticket3   = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/tickets" `
    -Method Post `
    -Headers @{ Authorization = "Bearer $token" } `
    -ContentType "application/json" `
    -Body $body

$ticket3Id = $ticket3.id
Write-Host "Ticket 3 ID: $ticket3Id"
```

---

#### Update a Ticket

```
PUT /api/v1/tickets/{ticket_id}
```

**Update Ticket 1**

```powershell
$body = @{
    customer_name  = "John Smith"
    customer_email = "john.smith@example.com"
    issue          = "Unable to login after password reset. Error: Invalid token."
    status         = "in_progress"
    assigned_agent = "support-agent-1"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/tickets/$ticket1Id" `
    -Method Put `
    -Headers @{ Authorization = "Bearer $token" } `
    -ContentType "application/json" `
    -Body $body
```

**Update Ticket 2**

```powershell
$body = @{
    customer_name  = "Sarah Johnson"
    customer_email = "sarah.johnson@example.com"
    issue          = "Payment deducted twice. Customer requesting refund."
    status         = "resolved"
    assigned_agent = "finance-agent-1"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/tickets/$ticket2Id" `
    -Method Put `
    -Headers @{ Authorization = "Bearer $token" } `
    -ContentType "application/json" `
    -Body $body
```

**Update Ticket 3**

```powershell
$body = @{
    customer_name  = "Michael Brown"
    customer_email = "michael.brown@example.com"
    issue          = "Analytics dashboard loads slowly after update."
    status         = "in_progress"
    assigned_agent = "operations-agent-1"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/tickets/$ticket3Id" `
    -Method Put `
    -Headers @{ Authorization = "Bearer $token" } `
    -ContentType "application/json" `
    -Body $body
```

---

### Prometheus Metrics

```
GET /metrics
```

```powershell
Invoke-WebRequest `
    -Uri "http://localhost:8000/metrics" `
    -UseBasicParsing `
    | Select-Object -ExpandProperty Content
```

Grafana is available at `http://localhost:3000` (default credentials: `admin / admin`).

---

## Database Verification

Connect to PostgreSQL:

```powershell
docker exec -it automation-postgres psql -U postgres -d automation_db
```

**Workflows**

```sql
SELECT * FROM workflows;

SELECT workflow_name, workflow_type, status
FROM workflows;
```

**Workflow Tasks**

```sql
-- Count tasks for a specific workflow
SELECT
    workflow_id,
    COUNT(*) AS task_count
FROM workflow_tasks
WHERE workflow_id = 'PASTE_WORKFLOW_ID_HERE'
GROUP BY workflow_id;

-- Check agent assigned to a workflow
SELECT
    workflow_id,
    assigned_agent,
    status
FROM workflow_tasks
WHERE workflow_id = 'PASTE_WORKFLOW_ID_HERE';
```

**Agents**

```sql
SELECT
    id,
    agent_name,
    agent_type,
    status,
    capabilities,
    last_active
FROM agents;

-- Inspect a single agent
SELECT
    id,
    agent_name,
    agent_type,
    status,
    capabilities,
    last_active
FROM agents
WHERE id = 'PASTE_AGENT_ID_HERE';
```

**Support Tickets**

```sql
SELECT
    id,
    customer_name,
    issue,
    sentiment,
    assigned_agent,
    status,
    created_at
FROM support_tickets;

-- Inspect a single ticket
SELECT
    id,
    customer_name,
    status,
    assigned_agent,
    issue
FROM support_tickets
WHERE id = 'PASTE_TICKET_ID_HERE';
```

---

## Workflow Lifecycle

```mermaid
stateDiagram-v2
    [*] --> PENDING
    PENDING --> RUNNING
    RUNNING --> COMPLETED
    RUNNING --> FAILED
    RUNNING --> PAUSED
    PAUSED --> RUNNING : resume
    FAILED --> RUNNING : retry
    COMPLETED --> RUNNING : retry
    COMPLETED --> [*]
```

| Action    | Description                                                  |
|-----------|--------------------------------------------------------------|
| trigger   | Enqueues the workflow in Celery and returns immediately       |
| execute   | Runs the workflow synchronously and blocks for the result    |
| pause     | Suspends an active workflow                                  |
| resume    | Continues a paused workflow                                  |
| retry     | Re-executes a failed or completed workflow from scratch       |

---

## Agent Assignment Map

Each workflow type dispatches to a specific set of agents:

| Workflow Type | Agents Assigned                  |
|---------------|----------------------------------|
| finance       | Finance Agent, Analytics Agent   |
| analytics     | Analytics Agent                  |
| support       | Support Agent, Operations Agent  |
| operations    | Operations Agent                 |

To inspect agent assignments for a specific workflow:

```sql
SELECT
    workflow_id,
    assigned_agent,
    status
FROM workflow_tasks
WHERE workflow_id = 'PASTE_WORKFLOW_ID_HERE';
```
