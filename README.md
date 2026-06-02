# Multi-Agent Business Automation System

Production-oriented backend platform for finance, analytics, operations, and customer support automation using autonomous agents coordinated through FastAPI, LangGraph, CrewAI, AutoGen, PostgreSQL, Redis, Celery, Prometheus, and Grafana.

## Architecture

```mermaid
graph TB
    Client["Clients / Dashboards"]
    GW["FastAPI API Gateway<br/>JWT | RBAC | Rate Limit"]
    Auth["Auth Service<br/>Login | Register | Token"]
    WF["Workflow Service<br/>CRUD | Trigger | Execute"]
    WFO["Workflow Orchestrator<br/>LangGraph State Machine"]
    AgentSvc["Agent Service<br/>Finance | Analytics<br/>Support | Operations"]
    Agents["Agent Framework<br/>CrewAI | AutoGen | LangGraph"]
    DB["PostgreSQL<br/>Users | Workflows | Tickets"]
    Cache["Redis Cache<br/>Session | Rate Limit | Pub/Sub"]
    Queue["Celery Queue<br/>Distributed Tasks"]
    Monitor["Prometheus<br/>Metrics & Monitoring"]
    Grafana["Grafana Dashboard<br/>Visualization & Alerts"]
    
    Client -->|HTTP/WS| GW
    GW --> Auth
    GW --> WF
    WF --> WFO
    WFO --> AgentSvc
    AgentSvc --> Agents
    Agents --> Cache
    WFO --> Queue
    Queue --> Agents
    Auth --> DB
    WF --> DB
    WFO --> DB
    Agents --> Monitor
    GW --> Monitor
    Monitor --> Grafana
    Cache -.->|Pub/Sub| Agents
    DB -.->|Async| Cache
```

The code is organized around thin API routers, service-layer business logic, repository-based persistence, and framework adapters for CrewAI, LangGraph, AutoGen, and LangChain-friendly future tooling.

## Features

- JWT authentication with role-based access control: Admin, Manager, Analyst, Support Executive
- Workflow CRUD plus trigger, inline execute, pause, resume, retry, and execution history
- Finance, analytics, support, and operations agents with autonomous delegation
- LangGraph execution graph with conditional routing and parallel async agent execution
- CrewAI and AutoGen adapters with graceful local fallbacks
- PostgreSQL persistence through SQLAlchemy async sessions and Alembic migrations
- Redis for rate limiting, Pub/Sub, workflow state cache, and Celery broker/backend
- Celery workers for distributed background execution
- Prometheus `/metrics`, structured JSON logs, health and readiness endpoints
- Docker Compose for local and production deployment
- Grafana dashboard provisioning
- Kubernetes starter manifests and GitHub Actions CI

## API Surface

All versioned endpoints are mounted under `/api/v1`.

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `POST /workflows`
- `GET /workflows`
- `GET /workflows/{id}`
- `PUT /workflows/{id}`
- `DELETE /workflows/{id}`
- `POST /workflows/{id}/trigger`
- `POST /workflows/{id}/execute`
- `POST /workflows/{id}/pause`
- `POST /workflows/{id}/resume`
- `POST /workflows/{id}/retry`
- `GET /agents`
- `GET /agents/{id}`
- `POST /agents/execute`
- `GET /analytics/overview`
- `GET /analytics/workflow-metrics`
- `GET /analytics/agent-performance`
- `POST /tickets`
- `GET /tickets`
- `PUT /tickets/{id}`
- `WS /notifications/workflows/{workflow_id}/ws`
- `GET /health`
- `GET /ready`

Swagger UI is available at `/docs`.

## Local Deployment

```bash
cp .env.example .env
docker-compose up --build
```

Run migrations:

```bash
docker-compose exec backend alembic upgrade head
```

Access services:

- FastAPI: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

Grafana defaults to `admin` / `admin` locally.

## Example Requests

Register a user:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Admin","email":"admin@example.com","password":"password123","role":"admin"}'
```

Login:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password123"}'
```

Create a finance workflow:

```bash
curl -X POST http://localhost:8000/api/v1/workflows \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "Monthly Expense Review",
    "workflow_type": "finance",
    "input_payload": {
      "expenses": [{"amount": 200}, {"amount": 1200}, {"amount": 250}],
      "include_forecast": true
    }
  }'
```

Queue workflow execution:

```bash
curl -X POST http://localhost:8000/api/v1/workflows/<workflow_id>/trigger \
  -H "Authorization: Bearer <token>"
```

Execute immediately without Celery:

```bash
curl -X POST http://localhost:8000/api/v1/workflows/<workflow_id>/execute \
  -H "Authorization: Bearer <token>"
```

## Production Deployment

Configure `.env` with production values:

```env
ENVIRONMENT=production
DATABASE_URL=postgresql://postgres:password@db:5432/automation_db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=replace_with_a_long_random_production_secret
OPENAI_API_KEY=your_openai_key
```

Start the production stack:

```bash
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

For HTTPS, point a host at the VPS and terminate TLS with Certbot/Nginx:

```bash
sudo apt update
sudo apt install docker.io docker-compose nginx certbot python3-certbot-nginx
sudo certbot --nginx
```

## Kubernetes

Build and publish the image, create an `automation-secrets` Kubernetes secret with the environment variables, then apply:

```bash
kubectl apply -f k8s/
kubectl get pods
kubectl get services
```

## Development

Install dependencies locally:

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
```

Run checks:

```bash
ruff check app tests
pytest -q
```

Run the API locally:

```bash
uvicorn app.main:app --reload
```

Run a worker locally:

```bash
celery -A app.tasks.celery_app worker --loglevel=INFO -Q workflows
```

## File Structure

```
multi-agent-business-automation-system-build/
├── app/                          # Main application package
│   ├── main.py                   # FastAPI app initialization & middleware setup
│   ├── tasks.py                  # Celery task definitions for distributed execution
│   ├── api/                      # API route handlers
│   │   ├── v1/
│   │   │   ├── router.py         # Main router - mounts all v1 endpoints
│   │   │   ├── auth.py           # Authentication endpoints (login, register, me)
│   │   │   ├── workflows.py      # Workflow CRUD & execution (trigger, pause, resume)
│   │   │   ├── agents.py         # Agent registry & execution
│   │   │   ├── analytics.py      # Analytics & metrics endpoints
│   │   │   ├── tickets.py        # Support ticket management
│   │   │   ├── notifications.py  # WebSocket notifications
│   │   │   └── health.py         # Health & readiness checks
│   │   └── deps.py               # Dependency injection & security
│   ├── agents/                   # AI Agent implementations
│   │   ├── base.py               # Abstract base agent class
│   │   ├── finance.py            # Finance automation agent
│   │   ├── analytics.py          # Analytics agent
│   │   ├── support.py            # Support & ticket agent
│   │   ├── operations.py         # Operations automation agent
│   │   ├── registry.py           # Agent registry & factory
│   │   ├── crew_adapter.py       # CrewAI framework adapter
│   │   └── autogen_adapter.py    # AutoGen framework adapter
│   ├── workflows/                # Workflow orchestration (LangGraph)
│   │   ├── state.py              # Workflow state definitions
│   │   └── langgraph_orchestrator.py  # LangGraph state machine & routing
│   ├── services/                 # Business logic layer
│   │   ├── auth_service.py       # Authentication & JWT logic
│   │   ├── workflow_service.py   # Workflow management logic
│   │   ├── agent_service.py      # Agent execution & coordination
│   │   ├── analytics_service.py  # Analytics aggregation
│   │   ├── ticket_service.py     # Support ticket processing
│   │   └── notification_service.py # Real-time notifications
│   ├── repositories/             # Data access layer (Repository pattern)
│   │   ├── base.py               # Generic async repository base
│   │   ├── users.py              # User CRUD operations
│   │   ├── workflows.py          # Workflow persistence
│   │   ├── agents.py             # Agent metadata storage
│   │   ├── tickets.py            # Support ticket storage
│   │   └── analytics.py          # Analytics data queries
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── user.py               # User model with roles
│   │   ├── workflow.py           # Workflow definition & execution tracking
│   │   ├── workflow_task.py      # Workflow task steps
│   │   ├── agent.py              # Agent metadata
│   │   ├── support_ticket.py     # Support ticket model
│   │   ├── analytics_report.py   # Analytics report storage
│   │   └── enums.py              # Status, role, and type enums
│   ├── schemas/                  # Pydantic request/response models
│   │   ├── auth.py               # Auth request/response schemas
│   │   ├── user.py               # User schemas
│   │   ├── workflow.py           # Workflow request/response schemas
│   │   ├── agent.py              # Agent schemas
│   │   ├── ticket.py             # Ticket schemas
│   │   ├── analytics.py          # Analytics schemas
│   │   └── common.py             # Common/shared schemas
│   ├── core/                     # Configuration & utilities
│   │   ├── config.py             # Settings from environment
│   │   ├── security.py           # JWT token & password hashing
│   │   ├── logging.py            # Structured JSON logging
│   │   └── exceptions.py         # Custom exception types
│   ├── db/                       # Database & cache setup
│   │   ├── session.py            # SQLAlchemy async session factory
│   │   ├── base.py               # Declarative base & metadata
│   │   └── redis.py              # Redis connection & utilities
│   ├── middleware/               # HTTP middleware
│   │   ├── request_context.py    # Request context tracking
│   │   └── rate_limit.py         # Rate limiting middleware
│   ├── monitoring/               # Observability
│   │   └── metrics.py            # Prometheus metrics definitions
│   └── utils/                    # Utility functions
├── alembic/                      # Database migrations (SQLAlchemy)
│   ├── versions/                 # Migration scripts
│   └── env.py                    # Migration configuration
├── tests/                        # Unit & integration tests
│   ├── test_*.py                 # Test modules
│   └── conftest.py               # Pytest fixtures
├── docker/                       # Docker build scripts
│   └── Dockerfile.*.txt          # Service-specific Dockerfiles (optional)
├── k8s/                          # Kubernetes manifests
│   ├── deployment.yaml           # FastAPI deployment
│   ├── worker.yaml               # Celery worker deployment
│   ├── service.yaml              # Service exposure
│   ├── ingress.yaml              # Ingress routing
│   ├── configmap.yaml            # Environment configuration
│   └── secrets.yaml              # Secret management
├── nginx/                        # Nginx reverse proxy config
│   └── nginx.conf                # Proxy, SSL, routing configuration
├── prometheus/                   # Prometheus configuration
│   └── prometheus.yml            # Metrics scrape config
├── grafana/                      # Grafana provisioning
│   ├── provisioning/dashboards/  # Dashboard JSON definitions
│   └── provisioning/datasources/ # Data source configurations
├── .github/workflows/            # GitHub Actions CI/CD
│   ├── test.yml                  # Run tests & linting on PR
│   └── deploy.yml                # Deploy on main branch
├── docker-compose.yml            # Local dev environment
├── docker-compose.prod.yml       # Production deployment
├── Dockerfile                    # FastAPI app Docker image
├── pyproject.toml                # Python project config & dependencies
├── requirements.txt              # Python dependencies
├── alembic.ini                   # Alembic configuration
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## Execution Workflow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI as FastAPI Gateway
    participant Auth as Auth Service
    participant WF as Workflow Service
    participant Orch as LangGraph Orchestrator
    participant Agent as Agent Service
    participant Queue as Celery Queue
    participant DB as PostgreSQL
    participant Cache as Redis Cache
    participant Metrics as Prometheus
    
    Client->>FastAPI: POST /workflows (create)
    FastAPI->>Auth: Verify JWT token
    Auth-->>FastAPI: Token valid
    FastAPI->>WF: Store workflow definition
    WF->>DB: Save workflow record
    DB-->>WF: Workflow ID
    WF-->>FastAPI: Workflow created (202)
    FastAPI-->>Client: Return workflow ID
    
    Client->>FastAPI: POST /workflows/{id}/trigger (queue execution)
    FastAPI->>Auth: Verify JWT token
    FastAPI->>Orch: Queue workflow execution
    Orch->>Queue: Add task to Celery queue
    Queue-->>Orch: Task acknowledged
    Orch->>DB: Update status to QUEUED
    Orch-->>FastAPI: Task ID
    FastAPI-->>Client: Return task ID (202)
    
    Queue->>Agent: Dequeue & execute workflow
    Agent->>Orch: Initialize workflow state
    Orch->>Agent: Route to appropriate agent (Finance/Analytics/Support/Operations)
    Agent->>Cache: Check cached dependencies
    Agent->>Agent: Execute business logic
    Agent->>Metrics: Record execution metrics
    Agent->>DB: Store execution results
    DB-->>Agent: Confirmed
    Agent->>Cache: Update result cache
    Agent-->>Orch: Execution complete
    Orch->>DB: Update workflow status to COMPLETED
    
    Client->>FastAPI: GET /workflows/{id} (poll status)
    FastAPI->>DB: Fetch workflow record
    DB-->>FastAPI: Workflow data + results
    FastAPI-->>Client: Return workflow data (200)
    
    Client->>FastAPI: WS /notifications/workflows/{id}/ws (subscribe)
    FastAPI->>Cache: Subscribe to Pub/Sub channel
    Cache-->>FastAPI: Subscription confirmed
    Agent->>Cache: Publish execution update
    Cache->>FastAPI: Broadcast update
    FastAPI-->>Client: Send WebSocket message
```

## Request Processing Flow

```mermaid
graph LR
    A["HTTP Request"] -->|middleware| B["Request Context<br/>Logging"]
    B -->|middleware| C["Rate Limit<br/>Check"]
    C -->|JWT validation| D["Security Layer<br/>Token Extraction"]
    D -->|authorized| E["Route Handler<br/>Dependency Injection"]
    E -->|get user| F["Auth Service"]
    E -->|business logic| G["Workflow/Agent/Ticket<br/>Service"]
    F -->|query| H["User Repository"]
    G -->|query/update| I["Workflow/Agent/Ticket<br/>Repository"]
    H -->|SQL| J["PostgreSQL"]
    I -->|SQL| J
    G -->|cache| K["Redis Cache"]
    G -->|async| L["Celery Queue"]
    G -->|emit| M["Prometheus Metrics"]
    J -.->|results| G
    K -.->|cached data| G
    G -->|response| N["Response Schema<br/>Validation"]
    N -->|success| O["HTTP Response 200"]
    C -->|rate limited| P["HTTP Response 429"]
    D -->|unauthorized| Q["HTTP Response 401"]
    E -->|validation error| R["HTTP Response 422"]
```

## Agent Execution Flow

```mermaid
stateDiagram-v2
    [*] --> Initialize
    Initialize --> RouteAgent: Determine agent type
    
    RouteAgent --> Finance: workflow_type == 'finance'
    RouteAgent --> Analytics: workflow_type == 'analytics'
    RouteAgent --> Support: workflow_type == 'support'
    RouteAgent --> Operations: workflow_type == 'operations'
    
    Finance --> LoadContext: Load workflow input<br/>& context data
    Analytics --> LoadContext
    Support --> LoadContext
    Operations --> LoadContext
    
    LoadContext --> ExecuteAgent: Send to LLM or<br/>local fallback
    ExecuteAgent --> CrewAI: Framework: CrewAI
    ExecuteAgent --> AutoGen: Framework: AutoGen
    ExecuteAgent --> Deterministic: Framework: Local<br/>Fallback
    
    CrewAI --> ProcessOutput: Parse results
    AutoGen --> ProcessOutput
    Deterministic --> ProcessOutput
    
    ProcessOutput --> UpdateDB: Persist execution<br/>results
    UpdateDB --> PublishMetrics: Record metrics
    PublishMetrics --> Notify: Send WebSocket<br/>notification
    Notify --> [*]
```

## Notes on AI Frameworks

The platform exposes explicit integration points for:

- **LangGraph**: workflow state transitions, conditional routing, and parallel execution
- **CrewAI**: collaborative business-agent crews with role-based delegation
- **AutoGen**: conversational multi-agent execution with dynamic conversation
- **LangChain**: dependency included for future tool/RAG integrations

The code includes deterministic fallbacks so the backend remains testable and deployable even before external LLM credentials or production agent prompts are configured.
