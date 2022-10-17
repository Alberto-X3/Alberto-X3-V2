from __future__ import annotations


__all__ = ("apply_block_events_adapter",)


from sqlalchemy import Column, BigInteger
from typing import TYPE_CHECKING

from naff.api.events import RawGatewayEvent
from naff.client.utils import TTLCache

from AlbertUnruhUtils.utils.logger import get_logger

from .database import Base, db, db_context
from .stats import DailyStatsModel


if TYPE_CHECKING:
    from naff import Client
    from typing import Callable, Coroutine


logger = get_logger(__name__.split(".")[-1], level=None, add_handler=False)


# event blocker


class BlockedUserModel(Base):
    __tablename__ = "blocked_user"

    user: Column | int = Column(
        BigInteger, primary_key=True, unique=True, nullable=False
    )

    CACHE: TTLCache[int, bool] = TTLCache()
    """True if blocked"""

    @staticmethod
    async def block(user: int) -> bool:
        if not await BlockedUserModel.is_blocked(user):
            await db.add(BlockedUserModel(user=user))
            BlockedUserModel.CACHE[user] = True
            logger.info(f"Blocked {user} for future events")
            return True
        else:
            return False

    @staticmethod
    async def unblock(user: int) -> bool:
        if await BlockedUserModel.is_blocked(user):
            await db.delete(await db.get(BlockedUserModel, user=user))
            BlockedUserModel.CACHE[user] = False
            logger.info(f"Unblocked {user} for future events")
            return True
        else:
            return False

    @staticmethod
    async def is_blocked(user: int) -> bool:
        if (is_blocked := BlockedUserModel.CACHE.get(user)) is not None:
            return is_blocked
        is_blocked = await db.get(BlockedUserModel, user=user) is not None
        BlockedUserModel.CACHE[user] = is_blocked
        return is_blocked


class BlockEventsAdapter:
    processor: Callable[[RawGatewayEvent], Coroutine]

    def __init__(self, processor: Callable[[RawGatewayEvent], Coroutine]):
        self.processor = processor

    async def __call__(self, event: RawGatewayEvent):
        collected = set()

        # data[user_id]
        if (tmp := event.data.get("user_id")) is not None:
            collected.add(tmp)

        # data[author_id]
        if (tmp := event.data.get("author_id")) is not None:
            collected.add(tmp)

        # data[user][id]
        if (tmp := event.data.get("user")) is not None:
            if (tmp := tmp.get("id")) is not None:
                collected.add(tmp)

        # data[author][id]
        if (tmp := event.data.get("author")) is not None:
            if (tmp := tmp.get("id")) is not None:
                collected.add(tmp)

        async with db_context():
            for id in collected:  # noqa
                if await BlockedUserModel.is_blocked(int(id)):
                    logger.debug(f"Blocked dispatching Event: {event.resolved_name}")
                    return
            await DailyStatsModel.incr_events()  # sneak it into the new session ^^

        await self.processor(event)


def apply_block_events_adapter(bot: Client):
    logger.debug(
        f"Applying BlockEventsAdapter ({len(bot.processors)}x) to {', '.join(bot.processors.keys())}"
    )
    for name, processor in bot.processors.items():
        bot.processors[name] = BlockEventsAdapter(processor)
