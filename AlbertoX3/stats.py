from __future__ import annotations


__all__ = (
    "StatsModel",
    "StatsEnum",
    "DailyStatsModel",
    "try_increment",
)


import importlib

from aenum import EnumType
from datetime import datetime
from sqlalchemy import Column, String, BigInteger
from typing import TYPE_CHECKING

from AlbertUnruhUtils.utils.logger import get_logger

from .aio import run_as_task
from .enum import NoAliasEnum
from .database import Base, db, db_context


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
    async def incr(self) -> int:
        return (await StatsModel.incr(self.fullname)).value

    async def reset(self) -> int:
        stats = await StatsModel.get(self.fullname)
        stats.value = 0
        return 0


class DailyStatsModel(Base):
    __tablename__ = "daily_stats"

    # format: YYYY-MM-DD (has a length of 10)
    date: Column | str = Column(
        String(10), primary_key=True, unique=True, nullable=False
    )
    value: Column | int = Column(BigInteger, nullable=False)

    @staticmethod
    async def get(date: Optional[datetime, str] = None) -> DailyStatsModel:
        if date is None:
            date = datetime.utcnow()
        if isinstance(date, datetime):
            date = date.strftime("%Y-%m-%d")
        if (stats := await db.get(DailyStatsModel, date=date)) is None:
            return await db.add(DailyStatsModel(date=date, value=0))
        return stats

    @staticmethod
    async def incr(
        date: Optional[datetime, str] = None, value: int = 1
    ) -> DailyStatsModel:
        stats = await DailyStatsModel.get(date)
        stats.value += value
        return stats


@run_as_task
async def try_increment(module: ModuleType, context: dContext) -> bool:
    """
    Tries to increment a Stat for a Module.
    """
    stats: Optional[StatsEnum]

    # first daily stats, then individual stats
    async with db_context():
        value = (await DailyStatsModel.incr()).value
    logger.info(f"Incremented daily stats ({value})")

    # now the individual stats (if there are such)
    if (stats := getattr(module, "Stats", None)) is None:
        try:
            module = importlib.import_module(".stats", module.__package__)
            stats = getattr(module, "Stats", None)
        except ImportError:
            pass

    if stats is None:
        logger.info(f"Can't find 'Stats' for {module.__name__!r}!")
        return False

    if not isinstance(stats, EnumType):
        logger.warning(
            f"{module.__name__+'.Stats'!r} is not an instance of 'StatsEnum', "
            f"received an instance of {stats.__class__.__name__!r} instead!"
        )
        return False

    if (
        enum := getattr(stats, context.invoked_name, None)
    ) is None or enum.value is False:
        logger.info(
            f"{module.__name__+'.Stats'!r} is either deactivated or not set,"
            f"so it will be ignored."
        )
        return False

    if not isinstance(enum, StatsEnum):
        logger.warning(
            f"{module.__name__+'.Stats'!r} is not an instance of 'StatsEnum', "
            f"received an instance of {stats.__class__.__name__!r} instead!"
        )
        return False

    async with db_context():
        value = await enum.incr()

    logger.info(
        f"Incremented stats for {context.invoked_name!r} in {module.__package__!r} ({value})"
    )
    return True
