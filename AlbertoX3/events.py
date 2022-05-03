from __future__ import annotations


__all__ = ("apply_block_events_adapter",)


from asyncio import gather
from sqlalchemy import Column, BigInteger
from typing import TYPE_CHECKING

from dis_snek.api.events import RawGatewayEvent
from dis_snek.client.utils import TTLCache

from AlbertUnruhUtils.utils.logger import get_logger

from .config import Config
from .database import Base, db, db_context
from .stats import DailyStatsModel
from . import listener


if TYPE_CHECKING:
    from dis_snek import Snake
    from typing import Callable, Coroutine, Set


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
        collected_ids: Set[int] = set()
        event_listeners: Set[listener.Channel] = set()

        # data[user_id]
        if (tmp := event.data.get("user_id")) is not None:
            collected_ids.add(int(tmp))

        # data[author_id]
        if (tmp := event.data.get("author_id")) is not None:
            collected_ids.add(int(tmp))

        # data[user][id]
        if (tmp := event.data.get("user")) is not None:
            if (tmp := tmp.get("id")) is not None:
                collected_ids.add(int(tmp))

        # data[author][id]
        if (tmp := event.data.get("author")) is not None:
            if (tmp := tmp.get("id")) is not None:
                collected_ids.add(int(tmp))

        async with db_context():

            await DailyStatsModel.incr_events()  # sneak it into the new session ^^

            for id in collected_ids:  # noqa

                # event by a contributor
                if id in map(lambda x: x.discord_id, Config.CONTRIBUTORS):
                    event_listeners.add(listener.event_contributor_event)
                # event by the owner
                if id == Config.AUTHOR.discord_id:
                    # the owner has the right to do everything ^^
                    continue

                if await BlockedUserModel.is_blocked(id):
                    logger.debug(f"Blocked dispatching Event: {event.resolved_name}")

                    # message create  (due to moderation)
                    if event.resolved_name == "raw_message_create":
                        event_listeners.add(listener.blocked_event_message_create)
                    # message update  (due to moderation)
                    if event.resolved_name == "raw_message_update":
                        event_listeners.add(listener.blocked_event_message_update)
                    # message delete  (due to moderation)
                    if event.resolved_name == "raw_message_delete":
                        event_listeners.add(listener.blocked_event_message_delete)
                    # guild member add  (due to nickname-managing/join message)
                    if event.resolved_name == "raw_guild_member_add":
                        event_listeners.add(listener.blocked_event_guild_member_add)
                    # guild member update  (due to nickname-managing)
                    if event.resolved_name == "raw_guild_member_update":
                        event_listeners.add(listener.blocked_event_guild_member_update)
                    # guild member remove  (due to leave message)
                    if event.resolved_name == "raw_guild_member_remove":
                        event_listeners.add(listener.blocked_event_guild_member_remove)

                    await gather(*[el(event) for el in event_listeners])

                    return

        event_listeners.add(self.processor)  # type: ignore

        await gather(*[el(event) for el in event_listeners])


def apply_block_events_adapter(bot: Snake):
    logger.debug(
        f"Applying BlockEventsAdapter ({len(bot.processors)}x) to {', '.join(bot.processors.keys())}"
    )
    for name, processor in bot.processors.items():
        bot.processors[name] = BlockEventsAdapter(processor)
