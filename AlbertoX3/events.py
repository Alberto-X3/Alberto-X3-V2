from __future__ import annotations


__all__ = ("apply_block_events_adapter",)


from sqlalchemy import Column, BigInteger
from typing import TYPE_CHECKING

from dis_snek.api.events import RawGatewayEvent
from dis_snek.client.utils import TTLCache

from AlbertUnruhUtils.utils.logger import get_logger

from .database import Base, db, db_context


if TYPE_CHECKING:
    from dis_snek import Snake
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

        if collected:  # don't create *every* time a new db-session
            async with db_context():
                for id in collected:  # noqa
                    if await BlockedUserModel.is_blocked(int(id)):
                        return

        await self.processor(event)


def apply_block_events_adapter(bot: Snake):
    logger.debug(f"Applying BlockEventsAdapter to {', '.join(bot.processors.keys())}")
    for name, processor in bot.processors.items():
        bot.processors[name] = BlockEventsAdapter(processor)
