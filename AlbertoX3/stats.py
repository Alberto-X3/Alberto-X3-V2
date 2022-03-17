from __future__ import annotations


__all__ = (
    "StatsEnum",
    "try_increment",
)


import importlib

from sqlalchemy import Column, String, BigInteger
from typing import TYPE_CHECKING

from AlbertUnruhUtils.utils.logger import get_logger

from .aio import run_as_task
from .enum import NoAliasEnum
from .database import Base, db


if TYPE_CHECKING:
    from dis_snek import Context as dContext
    from types import ModuleType
    from typing import Optional


logger = get_logger(__name__.split(".")[-1], level=None, add_handler=False)


class StatsModel(Base):
    __tablename__ = "stats"

    name: Column | str = Column(
        String(128), primary_key=True, unique=True, nullable=False
    )
    value: Column | int = Column(BigInteger, nullable=False)

    @staticmethod
    async def get(name: str) -> StatsModel:
        if (stats := await db.get(StatsModel, name=name)) is None:
            return await db.add(StatsModel(name=name, value=0))
        return stats

    @staticmethod
    async def incr(name: str, value: int = 1) -> StatsModel:
        stats = await StatsModel.get(name)
        stats.value += value
        return stats


class StatsEnum(NoAliasEnum):
    @property
    async def incr(self) -> int:
        return (await StatsModel.incr(self.fullname)).value

    async def reset(self) -> int:
        stats = await StatsModel.get(self.fullname)
        stats.value = 0
        return 0


@run_as_task
async def try_increment(module: ModuleType, context: dContext):
    """
    Tries to increment a Stat for a Module in background.
    """
    stats: Optional[StatsEnum] = getattr(module, "Stats", None)

    if stats is None:
        try:
            module = importlib.import_module(".stats", module.__package__)
            stats = getattr(module, "Stats", None)
        except ImportError:
            pass

    if stats is None:
        logger.info(f"Can't find `Stats` for {module.__name__!r}!")
        return

    # ToDo: actual incrementing
