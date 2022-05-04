from __future__ import annotations


__all__ = (
    "ActivityScale",
    "setup",
)


import asyncio

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from dis_snek.client.errors import NotFound
from dis_snek.models.discord.enums import ChannelTypes
from dis_snek import (
    Embed,
    Permissions,
)

from AlbertoX3.adis_snek import Scale
from AlbertoX3.aio import run_as_task, event_loop, semaphore_gather
from AlbertoX3.database import db_wrapper
from AlbertoX3.translations import t

from .colors import Colors
from .models import ActivityModel


if TYPE_CHECKING:
    from dis_snek import (
        Snake,
        Message,
        Member,
        MessageContext,
        InteractionContext,
        Guild,
        GuildText,
        Timestamp,
    )
    from typing import List, Dict


tg = t.g
t = t.activity


class ActivityScale(Scale):
    @staticmethod
    @run_as_task
    async def scan(ctx: MessageContext | InteractionContext, days: int):
        async def update_status(msg: Message, content: str):
            embed.description = content
            embed.timestamp = datetime.utcnow()
            try:
                await msg.edit(embed=embed)
            except NotFound:
                msg = await msg.channel.send(embed=embed)
            return msg

        embed = Embed(title=t.scanning, timestamp=datetime.utcnow())
        # only index present will be 0
        message: List[Message] = [await ctx.send(embed=embed)]
        guild: Guild = ctx.guild
        members: Dict[Member, Timestamp] = {}
        active: Dict[GuildText, int] = {}
        completed: List[GuildText] = []

        async def update_progress():
            while len(completed) < len(channels):
                content = t.scanning_channel(
                    done=len(completed), all=len(channels), cnt=len(active)
                )
                for c, d in active.copy().items():
                    age = (
                        datetime.utcnow().replace(tzinfo=timezone.utc) - c.created_at
                    ).days
                    content += (
                        f"\n:small_orange_diamond: {c.mention} ({d} / {min(age, days)})"
                    )
                message[0] = await update_status(message[0], content)
                await asyncio.sleep(2)

        async def update_members(c: GuildText):
            active[c] = 0

            msg: Message
            async for msg in c.history(limit=None):
                s = (
                    datetime.utcnow().replace(tzinfo=timezone.utc) - msg.created_at
                ).total_seconds()
                if s > days * 24 * 60 * 60:
                    break
                members[msg.author] = max(
                    members.get(msg.author, msg.created_at), msg.created_at
                )
                active[c] = int(s / (24 * 60 * 60))

            del active[c]
            completed.append(c)

        channels: List[GuildText] = []
        permissions: Permissions
        for channel in filter(
            lambda c: c.type == ChannelTypes.GUILD_TEXT, guild.channels
        ):
            permissions = channel.permissions_for(guild.me)
            if permissions.VIEW_CHANNEL and permissions.READ_MESSAGE_HISTORY:
                channels.append(channel)

        task = event_loop.create_task(update_progress())
        try:
            await semaphore_gather(10, *map(update_members, channels))
        finally:
            task.cancel()

        await update_status(message[0], t.scan_complete(cnt=len(channels)))

        embed = Embed(title=t.updating_members)
        message: Message = await ctx.send(embed=embed)

        await semaphore_gather(
            10,
            *[
                db_wrapper(ActivityModel.update)(m.id, ts.timestamp())
                for m, ts in members.items()
            ],
        )
        await update_status(message, t.updated_members(cnt=len(members)))


def setup(bot: Snake):
    ActivityScale(bot)
