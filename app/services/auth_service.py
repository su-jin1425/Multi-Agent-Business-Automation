from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError, NotFoundError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.users import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def register(self, payload: UserCreate) -> User:
        existing = await self.users.get_by_email(str(payload.email))
        if existing:
            raise AppError("Email is already registered", 409)
        user = await self.users.create(
            name=payload.name,
            email=str(payload.email).lower(),
            password_hash=hash_password(payload.password),
            role=payload.role,
        )
        await self.session.commit()
        return user

    async def authenticate(self, payload: LoginRequest) -> TokenResponse:
        user = await self.users.get_by_email(str(payload.email))
        if not user or not verify_password(payload.password, user.password_hash):
            raise AppError("Invalid email or password", 401)
        token = create_access_token(str(user.id), {"role": user.role.value, "email": user.email})
        return TokenResponse(access_token=token, user=user)

    async def get_user(self, user_id: str | UUID) -> User:
        user = await self.users.get(UUID(str(user_id)))
        if not user:
            raise NotFoundError("User")
        return user
