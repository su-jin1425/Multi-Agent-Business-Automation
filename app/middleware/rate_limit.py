import time

from fastapi import Request, Response, status
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis: Redis) -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self.redis = redis

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path.endswith("/health") or request.url.path.endswith("/metrics"):
            return await call_next(request)
        client = request.client.host if request.client else "unknown"
        window = int(time.time() // 60)
        key = f"rate-limit:{client}:{window}"
        count = await self.redis.incr(key)
        if count == 1:
            await self.redis.expire(key, 60)
        if count > settings.rate_limit_per_minute:
            return Response("Rate limit exceeded", status_code=status.HTTP_429_TOO_MANY_REQUESTS)
        return await call_next(request)
