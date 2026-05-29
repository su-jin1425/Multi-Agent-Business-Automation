from collections.abc import Sequence
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base


ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, item_id: UUID) -> ModelT | None:
        return await self.session.get(self.model, item_id)

    async def list(self, *, limit: int = 100, offset: int = 0) -> Sequence[ModelT]:
        result = await self.session.execute(select(self.model).offset(offset).limit(limit))
        return result.scalars().all()

    async def create(self, **values: object) -> ModelT:
        item = self.model(**values)
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def delete(self, item: ModelT) -> None:
        await self.session.delete(item)
        await self.session.flush()

    async def count(self, statement: Select[tuple[ModelT]] | None = None) -> int:
        stmt = statement or select(self.model)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())

