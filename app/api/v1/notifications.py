from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.db.redis import redis_client

router = APIRouter()


@router.websocket("/workflows/{workflow_id}/ws")
async def workflow_events(websocket: WebSocket, workflow_id: UUID) -> None:
    await websocket.accept()
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(f"workflow:{workflow_id}")
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_text(message["data"])
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe(f"workflow:{workflow_id}")
        await pubsub.close()
