# Multi-Agent Business Automation System

This document contains all PowerShell commands, SQL queries, workflow examples, agent execution examples, analytics verification steps, and support ticket operations required to fully test and validate the platform locally.

Source: Uploaded project testing document 

---

# Table of Contents

* Environment Setup
* Database Setup
* API Discovery
* Health Checks
* Authentication
* Workflow Management

  * Create Workflow
  * Read Workflow
  * Update Workflow
  * Delete Workflow
  * Trigger Workflow
  * Execute Workflow
  * Pause Workflow
  * Resume Workflow
  * Retry Workflow
* Agent Management
* Agent Execution
* Analytics APIs
* Metrics
* Support Ticket APIs
* PostgreSQL Verification Queries
* Endpoint Inventory

---

# Prerequisites

## Clone Repository

```powershell
git clone <repository-url>
cd automation-platform
```

## Create Environment File

```powershell
cp .env.example .env
```

---

# Start Application

Build and start all services:

```powershell
docker-compose up --build
```

---

# Run Database Migrations

```powershell
docker-compose exec backend alembic upgrade head
```

---

# Access PostgreSQL

```powershell
docker exec -it automation-postgres psql -U postgres -d automation_db
```

---

# API Discovery

## List All Endpoints

```powershell
$response = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/openapi.json"

$response.paths.PSObject.Properties |
ForEach-Object {
    [PSCustomObject]@{
        Path    = $_.Name
        Methods = ($_.Value.PSObject.Properties.Name -join ", ").ToUpper()
    }
} |
Sort-Object Path |
Format-Table -AutoSize
```

## Count Total Endpoints

```powershell
Write-Host ""
Write-Host "Total Endpoints:" (($response.paths.PSObject.Properties.Name).Count)
```

---

# Health Checks

## Health Endpoint

### GET /api/v1/health

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/health"
```

---

## Readiness Endpoint

### GET /api/v1/ready

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/ready"
```

---

# Authentication

---

## Register User

### POST /api/v1/auth/register

```powershell
$registerBody = @{
    name     = "Sujith"
    email    = "sujithssd14@gmail.com"
    password = "Password123!"
    role     = "admin"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/auth/register" `
    -Method Post `
    -ContentType "application/json" `
    -Body $registerBody
```

Available roles:

* ADMIN
* MANAGER
* ANALYST
* SUPPORT_EXECUTIVE

---

## Login

### POST /api/v1/auth/login

```powershell
$loginBody = @{
    email    = "sujithssd14@gmail.com"
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

---

## Verify Logged User

### GET /api/v1/auth/me

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/auth/me" `
    -Headers @{
        Authorization = "Bearer $token"
    }
```

---

# Workflow Management

---

## List Workflows

### GET /api/v1/workflows

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows" `
    -Method Get `
    -Headers @{
        Authorization = "Bearer $token"
    }
```

---

# Create Workflow

---

## Finance Workflow

```powershell
$body = @{
    workflow_name = "Monthly Expense Analysis"
    workflow_type = "finance"
    input_payload = @{
        expenses = @(
            @{
                department = "Engineering"
                amount = 50000
            },
            @{
                department = "Marketing"
                amount = 25000
            },
            @{
                department = "Operations"
                amount = 15000
            }
        )
    }
} | ConvertTo-Json -Depth 10

$financeWorkflow = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows" `
    -Method Post `
    -Headers @{
        Authorization = "Bearer $token"
    } `
    -ContentType "application/json" `
    -Body $body

$financeWorkflowId = $financeWorkflow.id

$financeWorkflowId
```

---

## Analytics Workflow

```powershell
$body = @{
    workflow_name = "Analytics Test"
    workflow_type = "analytics"
    input_payload = @{
        sales = @(120000,135000,142000)
    }
} | ConvertTo-Json -Depth 10

$analyticsWorkflow = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows" `
    -Method Post `
    -Headers @{
        Authorization = "Bearer $token"
    } `
    -ContentType "application/json" `
    -Body $body

$analyticsWorkflowId = $analyticsWorkflow.id
```

---

## Support Workflow

```powershell
$body = @{
    workflow_name = "Support Test"
    workflow_type = "support"
    input_payload = @{
        issue = "Unable to login after password reset"
    }
} | ConvertTo-Json -Depth 10

$supportWorkflow = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows" `
    -Method Post `
    -Headers @{
        Authorization = "Bearer $token"
    } `
    -ContentType "application/json" `
    -Body $body

$supportWorkflowId = $supportWorkflow.id
```

---

## Operations Workflow

```powershell
$body = @{
    workflow_name = "Operations Test"
    workflow_type = "operations"
    input_payload = @{
        tasks = @(
            "Generate Report",
            "Send Email",
            "Create Dashboard"
        )
    }
} | ConvertTo-Json -Depth 10

$operationsWorkflow = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows" `
    -Method Post `
    -Headers @{
        Authorization = "Bearer $token"
    } `
    -ContentType "application/json" `
    -Body $body

$operationsWorkflowId = $operationsWorkflow.id
```

---

# PostgreSQL Verification

```sql
SELECT * FROM workflows;
```

```sql
SELECT workflow_name,
       workflow_type,
       status
FROM workflows;
```

---

# Get Workflow

### GET /api/v1/workflows/{workflow_id}

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows/$financeWorkflowId" `
    -Headers @{
        Authorization = "Bearer $token"
    }
```

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows/$analyticsWorkflowId" `
    -Headers @{
        Authorization = "Bearer $token"
    }
```

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows/$supportWorkflowId" `
    -Headers @{
        Authorization = "Bearer $token"
    }
```

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows/$operationsWorkflowId" `
    -Headers @{
        Authorization = "Bearer $token"
    }
```

---

# Update Workflow

### PUT /api/v1/workflows/{workflow_id}

```powershell
$body = @{
    workflow_name = "Updated Expense Analysis"
    workflow_type = "finance"
    input_payload = @{
        expenses = @(
            @{
                department = "Engineering"
                amount = 75000
            },
            @{
                department = "Marketing"
                amount = 35000
            }
        )
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows/$financeWorkflowId" `
    -Method Put `
    -Headers @{
        Authorization = "Bearer $token"
    } `
    -ContentType "application/json" `
    -Body $body
```

---

# Trigger Workflow

### POST /api/v1/workflows/{workflow_id}/trigger

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows/$financeWorkflowId/trigger" `
    -Method Post `
    -Headers @{
        Authorization = "Bearer $token"
    }
```

Expected state flow:

```text
PENDING
   ↓
RUNNING
   ↓
COMPLETED
```

or

```text
FAILED
```

---

# Execute Workflow

### POST /api/v1/workflows/{workflow_id}/execute

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows/$financeWorkflowId/execute" `
    -Method Post `
    -Headers @{
        Authorization = "Bearer $token"
    }
```

### Trigger vs Execute

| Endpoint   | Behavior              |
| ---------- | --------------------- |
| `/trigger` | Queues background job |
| `/execute` | Runs immediately      |
| `/trigger` | Returns instantly     |
| `/execute` | Waits for result      |

---

# Pause Workflow

### POST /api/v1/workflows/{workflow_id}/pause

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows/$operationsWorkflowId/pause" `
    -Method Post `
    -Headers @{
        Authorization = "Bearer $token"
    }
```

---

# Resume Workflow

### POST /api/v1/workflows/{workflow_id}/resume

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows/$operationsWorkflowId/resume" `
    -Method Post `
    -Headers @{
        Authorization = "Bearer $token"
    }
```

---

# Retry Workflow

### POST /api/v1/workflows/{workflow_id}/retry

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/workflows/$operationsWorkflowId/retry" `
    -Method Post `
    -Headers @{
        Authorization = "Bearer $token"
    }
```

---

# Verify Workflow Tasks

```sql
SELECT
    workflow_id,
    COUNT(*) AS task_count
FROM workflow_tasks
WHERE workflow_id = 'PASTE_WORKFLOW_ID_HERE'
GROUP BY workflow_id;
```

---

# Agent Management

---

## List Agents

### GET /api/v1/agents

```powershell
$agents = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/agents" `
    -Headers @{
        Authorization = "Bearer $token"
    }
```

---

## Store Agent IDs

```powershell
$financeAgentId = ($agents | Where-Object {$_.agent_type -eq "finance"}).id

$supportAgentId = ($agents | Where-Object {$_.agent_type -eq "support"}).id

$operationsAgentId = ($agents | Where-Object {$_.agent_type -eq "operations"}).id

$analyticsAgentId = ($agents | Where-Object {$_.agent_type -eq "analytics"}).id
```

---

## Display Agent IDs

```powershell
Write-Host "Finance Agent ID: $financeAgentId"
Write-Host "Support Agent ID: $supportAgentId"
Write-Host "Operations Agent ID: $operationsAgentId"
Write-Host "Analytics Agent ID: $analyticsAgentId"
```

---

## Verify Agents in PostgreSQL

```sql
SELECT
    id,
    agent_name,
    agent_type,
    status,
    capabilities
FROM agents;
```

---

# Execute Agents

### POST /api/v1/agents/execute

## Finance Agent

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/agents/execute" `
    -Method Post `
    -Headers @{
        Authorization = "Bearer $token"
    } `
    -ContentType "application/json" `
    -Body (
        @{
            agent_type = "finance"
            task = "Analyze monthly department expenses"
            context = @{
                expenses = @(
                    @{department="Engineering";amount=50000}
                    @{department="Marketing";amount=25000}
                    @{department="Operations";amount=15000}
                )
            }
        } | ConvertTo-Json -Depth 10
    )
```

---

## Analytics Agent

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/agents/execute" `
    -Method Post `
    -Headers @{
        Authorization = "Bearer $token"
    } `
    -ContentType "application/json" `
    -Body (
        @{
            agent_type = "analytics"
            task = "Analyze sales trends"
            context = @{
                sales = @(120000,135000,142000)
            }
        } | ConvertTo-Json -Depth 10
    )
```

---

# Analytics APIs

## Overview

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/analytics/overview" `
    -Headers @{
        Authorization = "Bearer $token"
    } |
ConvertTo-Json -Depth 10
```

---

## Workflow Metrics

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/analytics/workflow-metrics" `
    -Headers @{
        Authorization = "Bearer $token"
    } |
ConvertTo-Json -Depth 10
```

---

## Agent Performance

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/analytics/agent-performance" `
    -Headers @{
        Authorization = "Bearer $token"
    } |
ConvertTo-Json -Depth 10
```

---

# Metrics

### GET /metrics

```powershell
Invoke-WebRequest `
    -Uri "http://localhost:8000/metrics" `
    -UseBasicParsing |
Select-Object -ExpandProperty Content
```

---

# Support Ticket APIs

---

## List Tickets

### GET /api/v1/tickets

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/tickets" `
    -Headers @{
        Authorization = "Bearer $token"
    } |
Format-Table -AutoSize
```

---

## Create Ticket

### Ticket 1

```powershell
$body = @{
    customer_name  = "John Smith"
    customer_email = "john.smith@example.com"
    issue          = "Unable to login after password reset"
} | ConvertTo-Json

$ticket1 = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/tickets" `
    -Method Post `
    -Headers @{
        Authorization = "Bearer $token"
    } `
    -ContentType "application/json" `
    -Body $body

$ticket1Id = $ticket1.id
```

---

## Verify Tickets

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
```

---

## Update Ticket

### PUT /api/v1/tickets/{ticket_id}

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
    -Headers @{
        Authorization = "Bearer $token"
    } `
    -ContentType "application/json" `
    -Body $body
```

---

## Verify Ticket Update

```sql
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

# Workflow-Agent Mapping

```text
FINANCE WORKFLOW
├── Finance Agent
└── Analytics Agent

ANALYTICS WORKFLOW
└── Analytics Agent

SUPPORT WORKFLOW
├── Support Agent
└── Operations Agent

OPERATIONS WORKFLOW
└── Operations Agent
```

---

# Workflow Task Assignment Verification

```sql
SELECT
    workflow_id,
    assigned_agent,
    status
FROM workflow_tasks
WHERE workflow_id = 'PASTE_WORKFLOW_ID_HERE';
```

---