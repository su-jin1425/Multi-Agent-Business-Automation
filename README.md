# Multi-Agent Business Automation System

Production-oriented backend platform for finance, analytics, operations, and customer support automation using autonomous agents coordinated through FastAPI, LangGraph, CrewAI, AutoGen, PostgreSQL, Redis, Celery, Prometheus, and Grafana.

## Architecture

```text
Clients / Dashboards
       |
FastAPI API Gateway  -- JWT, RBAC, validation, rate limiting, OpenAPI
       |
Workflow Orchestrator -- LangGraph state routing, retries, pause/resume
       |
Agent Service -- Finance, Analytics, Support, Operations, Supervisor routing
       |
PostgreSQL + Redis -- persistence, cache, Pub/Sub, queues, session state
       |
Celery Workers -- distributed async workflow execution
       |
Prometheus + Grafana -- metrics, latency, failure rate, queue health
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

## Notes on AI Frameworks

The platform exposes explicit integration points for:

- LangGraph: workflow state transitions, conditional routing, and parallel execution
- CrewAI: collaborative business-agent crews
- AutoGen: conversational multi-agent execution
- LangChain: dependency included for future tool/RAG integrations

The code includes deterministic fallbacks so the backend remains testable and deployable even before external LLM credentials or production agent prompts are configured.

