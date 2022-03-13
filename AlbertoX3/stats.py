__all__ = ("Stats",)


from sqlalchemy import Column, String, BigInteger

from .enum import NoAliasEnum
from .database import Base, db


class StatsModel(Base):
    __tablename__ = "stats"

    name: Column | str = Column(
        String(128), primary_key=True, unique=True, nullable=False
    )
    value: Column | int = Column(BigInteger, nullable=False)

    @staticmethod
    async def get(name: str) -> "StatsModel":
        if (stats := await db.get(StatsModel, name=name)) is None:
            return await db.add(StatsModel(name=name, value=0))
        return stats

    @staticmethod
    async def incr(name: str, value: int = 1) -> "StatsModel":
        stats = await StatsModel.get(name)
        stats.value += value
        return stats


class Stats(NoAliasEnum):
    @property
    async def incr(self) -> int:
        return (await StatsModel.incr(self.fullname)).value

    async def reset(self) -> int:
        stats = await StatsModel.get(self.fullname)
        stats.value = 0
        return 0
