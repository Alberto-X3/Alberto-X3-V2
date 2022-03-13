__all__ = ("Settings",)


from sqlalchemy import Column, String
from typing import TypeVar, Type

from .aio import LockDeco
from .database import Base, db, redis
from .enum import NoAliasEnum
from .environment import CACHE_TTL


T = TypeVar("T")


class SettingsModel(Base):
    __tablename__ = "settings"

    key: Column | str = Column(
        String(64), primary_key=True, unique=True, nullable=False
    )
    value: Column | str = Column(String(256), nullable=False)

    @staticmethod
    async def _create(key: str, value: str | int | float | bool) -> "SettingsModel":
        if isinstance(value, bool):
            value = int(value)

        return await db.add(SettingsModel(key=key, value=str(value)))

    @staticmethod
    @LockDeco
    async def get(dtype: Type[T], key: str, default: T | None = None) -> T | None:
        if await redis.exists(r_key := f"settings::{key}"):
            out = await redis.get(r_key)
        else:
            if (row := await db.get(SettingsModel, key=key)) is None:
                if default is None:
                    return None
                row = await SettingsModel._create(key, default)
            out = row.value
            await redis.setex(r_key, CACHE_TTL, out)

        if dtype == bool:
            out = int(out)

        return dtype(out)

    @staticmethod
    @LockDeco
    async def set(dtype: Type[T], key: str, value: T) -> "SettingsModel":
        r_key = f"settings::{key}"
        if (row := await db.get(SettingsModel, key=key)) is None:
            row = await SettingsModel._create(key, value)
            await redis.setex(r_key, CACHE_TTL, row.value)
            return row

        if dtype == bool:
            value = int(value)

        row.value = str(value)
        await redis.setex(r_key, CACHE_TTL, row.value)
        return row


class Settings(NoAliasEnum):
    @property
    def type(self) -> Type[T]:
        return type(self.value)

    async def get(self) -> T:
        return await SettingsModel.get(self.type, self.fullname, self.default)

    async def set(self, value: T) -> T:
        await SettingsModel.get(self.type, self.fullname, value)
        return value

    async def reset(self) -> T:
        return await self.set(self.default)
