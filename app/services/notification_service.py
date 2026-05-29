import json
from typing import Any
from uuid import UUID

from redis.asyncio import Redis


class NotificationService:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def publish_workflow_event(self, workflow_id: UUID, event_type: str, payload: dict[str, Any]) -> None:
        message = json.dumps({"workflow_id": str(workflow_id), "event_type": event_type, "payload": payload})
        await self.redis.publish(f"workflow:{workflow_id}", message)
        await self.redis.publish("workflow-events", message)

    async def cache_workflow_state(self, workflow_id: UUID, state: dict[str, Any]) -> None:
        await self.redis.set(f"workflow-state:{workflow_id}", json.dumps(state, default=str), ex=3600)

    async def queue_size(self) -> int:
        return int(await self.redis.llen("celery") or 0)
