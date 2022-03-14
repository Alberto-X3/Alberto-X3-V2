from __future__ import annotations


__all__ = ("PermissionsModel",)


from sqlalchemy import Column, String, Integer

from .database import Base, db, redis
from .environment import CACHE_TTL


class PermissionsModel(Base):
    __tablename__ = "permissions"

    permission: Column | str = Column(
        String(64), primary_key=True, unique=True, nullable=False
    )
    level: Column | int = Column(Integer, nullable=False)

    @staticmethod
    async def create(permission: str, level: int) -> PermissionsModel:
        return await db.add(PermissionsModel(permission=permission, level=level))

    @staticmethod
    async def get(permission: str, default: int) -> int:
        if await redis.exists(r_key := f"permissions::{permission}"):
            return int(await redis.get(r_key))

        if (row := await db.get(PermissionsModel, permission=permission)) is None:
            row = await PermissionsModel.create(permission, default)

        await redis.setex(r_key, CACHE_TTL, row.level)

        return row.level

    @staticmethod
    async def set(permission: str, level: int) -> PermissionsModel:
        await redis.setex(f"permissions::{permission}", CACHE_TTL, level)

        if (row := await db.get(PermissionsModel, permission=permission)) is None:
            row = await PermissionsModel.create(permission, level)

        row.level = level

        return row
