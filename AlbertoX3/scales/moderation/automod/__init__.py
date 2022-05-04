from __future__ import annotations


__all__ = (
    "AutoMod",
    "setup",
)


import copy
import re

from typing import TYPE_CHECKING

from dis_snek.api.events.discord import (
    RawGatewayEvent,
    MessageCreate,
    MessageUpdate,
    MessageDelete,
    MemberAdd,
    MemberUpdate,
    MemberRemove,
)
from dis_snek import (
    to_snowflake,
    BaseMessage,
    Member,
    MISSING,
    listen,
)

from AlbertoX3.adis_snek import Scale
from AlbertoX3.aio import event_loop
from AlbertoX3.config import Config
from AlbertoX3.database import db, filter_by
from AlbertoX3.translations import t
from AlbertoX3 import listener

from .colors import Colors
from .models import BadWordsModel, ScamLinksModel


if TYPE_CHECKING:
    from dis_snek import Snake, Message


tg = t.g
t = t.automod


RE_WORD = re.compile(
    r"([^\u0000-\u0040\u005B-\u0060\u007B-\u00BF\u02B0-\u036F\u00D7\u00F7\u2000-\u2BFF])+",
)
RE_LINK = re.compile(
    r"((?:([a-z\d]\.|[a-z\d][a-z\d\-]{0,61}[a-z\d])\.)+)([a-z\d]{2,63}|[a-z\d][a-z\d\-]{0,61}[a-z\d])\.?",
)


class AutoMod(Scale):
    def __init__(self, *_, **__):
        listener.blocked_event_message_create.register(
            self.discrete_message_create,
        )
        listener.blocked_event_message_update.register(
            self.discrete_message_update,
        )
        listener.blocked_event_message_delete.register(
            self.discrete_message_delete,
        )
        listener.blocked_event_guild_member_add.register(
            self.discrete_guild_member_add,
        )
        listener.blocked_event_guild_member_update.register(
            self.discrete_guild_member_update,
        )
        listener.blocked_event_guild_member_remove.register(
            self.discrete_guild_member_remove,
        )

    @staticmethod
    async def get_scam_link_score(message: Message) -> int:
        return sum(
            [
                entry.weight
                async for entry in await db.stream(filter_by(ScamLinksModel))
                if entry.link
                in map(
                    lambda x: x.group(0).removeprefix("www."),
                    RE_LINK.finditer(message.content),
                )
            ]
        )

    @staticmethod
    async def get_bad_word_score(message: Message) -> int:
        return sum(
            [
                entry.weight
                async for entry in await db.stream(filter_by(BadWordsModel))
                if entry.link
                in map(
                    lambda x: x.group(0),
                    RE_WORD.finditer(message.content),
                )
            ]
        )

    @staticmethod
    async def manage_nickname(member: Member):
        ...  # ToDo: ask database for nickname-prefix and update it if necessary

    # the following methods won't communicate with the database

    async def discrete_message_create(self, event: RawGatewayEvent | MessageCreate):
        if isinstance(event, RawGatewayEvent):
            # code below copied from
            # dis_snek.api.events.processors.message_events._on_raw_message_create

            msg = self.bot.cache.place_message_data(event.data)
            if not msg._guild_id and event.data.get("guild_id"):  # noqa
                msg._guild_id = event.data["guild_id"]

            if not msg.author:
                # sometimes discord will only send an author ID, not the author. this catches that
                await self.bot.cache.fetch_channel(
                    to_snowflake(msg._channel_id)  # noqa
                ) if not msg.channel else msg.channel
                if msg._guild_id:  # noqa
                    await self.bot.cache.fetch_guild(
                        msg._guild_id  # noqa
                    ) if not msg.guild else msg.guild
                    await self.bot.cache.fetch_member(
                        msg._guild_id, msg._author_id  # noqa
                    )
                else:
                    await self.bot.cache.fetch_user(
                        to_snowflake(msg._author_id)  # noqa
                    )

            event = MessageCreate(msg)

        ...  # ToDo: run filter whether the message contains scam or bad words

    async def discrete_message_update(self, event: RawGatewayEvent | MessageUpdate):
        if isinstance(event, RawGatewayEvent):
            # code below copied from
            # dis_snek.api.events.processors.message_events._on_raw_message_update

            # a copy is made because the cache will update the original object in memory
            before = copy.copy(
                self.bot.cache.get_message(
                    event.data.get("channel_id"), event.data.get("id")
                )
            )
            after = self.bot.cache.place_message_data(event.data)

            event = MessageUpdate(before=before, after=after)

        ...  # ToDo: run filter whether the message contains scam or bad words
        ...  # ToDo: log the old message

    async def discrete_message_delete(self, event: RawGatewayEvent | MessageDelete):
        if isinstance(event, RawGatewayEvent):
            # code below copied from
            # dis_snek.api.events.processors.message_events._on_raw_message_delete

            message = self.bot.cache.get_message(
                event.data.get("channel_id"),
                event.data.get("id"),
            )

            if not message:
                message = BaseMessage.from_dict(event.data, self.bot)
            self.bot.cache.delete_message(event.data["channel_id"], event.data["id"])

            event = MessageDelete(message)

        ...  # ToDo: log the old message

    async def discrete_guild_member_add(self, event: RawGatewayEvent | MemberAdd):
        if isinstance(event, RawGatewayEvent):
            # code below copied from
            # dis_snek.api.events.processors.message_events._on_raw_guild_member_add

            g_id = event.data.pop("guild_id")
            member = self.bot.cache.place_member_data(g_id, event.data)

            event = MemberAdd(g_id, member)

        ...  # ToDo: create join message
        ...  # ToDo: manage nicknames

    async def discrete_guild_member_update(self, event: RawGatewayEvent | MemberUpdate):
        if isinstance(event, RawGatewayEvent):
            # code below copied from
            # dis_snek.api.events.processors.message_events._on_raw_guild_member_update

            g_id = event.data.pop("guild_id")
            user = self.bot.cache.place_user_data(event.data["user"])

            event = MemberRemove(g_id, self.bot.cache.get_member(g_id, user.id) or user)

        ...  # ToDo: manage nicknames

    async def discrete_guild_member_remove(self, event: RawGatewayEvent | MemberRemove):
        if isinstance(event, RawGatewayEvent):
            # code below copied from
            # dis_snek.api.events.processors.member_events._on_raw_guild_member_remove

            g_id = event.data.pop("guild_id")
            before = (
                copy.copy(self.bot.cache.get_member(g_id, event.data["user"]["id"]))
                or MISSING
            )

            event = MemberUpdate(
                g_id, before, self.bot.cache.place_member_data(g_id, event.data)
            )

        ...  # ToDo: create leave message

    # the following methods communicate with the database

    @listen()
    async def message_create(self, event: MessageCreate):
        await self.discrete_message_create(event)
        ...  # ToDo: update last activity for member

    @listen()
    async def message_update(self, event: MessageUpdate):
        await self.discrete_message_update(event)
        ...  # ToDo: update last activity for member

    @listen()
    async def message_delete(self, event: MessageDelete):
        await self.discrete_message_delete(event)
        ...  # placeholder for future plans

    @listen()
    async def guild_member_add(self, event: MemberAdd):
        await self.discrete_guild_member_add(event)
        ...  # ToDo: update last activity for member

    @listen()
    async def guild_member_update(self, event: MemberUpdate):
        await self.discrete_guild_member_update(event)
        ...  # placeholder for future plans

    @listen()
    async def guild_member_remove(self, event: MemberRemove):
        await self.discrete_guild_member_remove(event)
        ...  # placeholder for future plans


def setup(bot: Snake):
    AutoMod(bot)
    event_loop.create_task(BadWordsModel.sync_from_csv(Config.BAD_WORDS_CSV))
    event_loop.create_task(ScamLinksModel.sync_from_csv(Config.SCAM_LINKS_CSV))
