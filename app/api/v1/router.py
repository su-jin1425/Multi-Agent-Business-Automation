from fastapi import APIRouter

from app.api.v1 import agents, analytics, auth, health, notifications, tickets, workflows

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["support"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
