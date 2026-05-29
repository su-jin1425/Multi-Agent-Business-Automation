from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.core.logging import logger


class AppError(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, resource: str) -> None:
        super().__init__(f"{resource} not found", status.HTTP_404_NOT_FOUND)


class PermissionDeniedError(AppError):
    def __init__(self, message: str = "Permission denied") -> None:
        super().__init__(message, status.HTTP_403_FORBIDDEN)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(_: Request, exc: IntegrityError) -> JSONResponse:
        logger.warning("database_integrity_error", error=str(exc.orig))
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Resource conflicts with existing data"},
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(_: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": exc.errors()})

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", error=str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

