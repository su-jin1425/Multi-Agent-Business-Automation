from time import perf_counter
from uuid import uuid4

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = str(uuid4())
        structlog.contextvars.bind_contextvars(request_id=request_id, path=request.url.path)
        started = perf_counter()
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{perf_counter() - started:.4f}"
        structlog.contextvars.clear_contextvars()
        return response

