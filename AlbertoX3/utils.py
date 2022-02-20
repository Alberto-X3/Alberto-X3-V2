__all__ = ("get_member",)

import re
from typing import Union, Optional

from dis_snek.models import Context, User, Member
from dis_snek.errors import NotFound


async def get_member(
    ctx: Context,
    raw: Union[str, int, User, Member],
) -> Optional[Member]:
    # case: Member
    if isinstance(raw, Member):
        return raw

    # case: User
    if isinstance(raw, User):
        try:
            return await ctx.bot.get_member(raw.id, ctx.guild_id)
        except NotFound:
            return None

    # case: int
    if isinstance(raw, int) or raw.isnumeric():
        try:
            return await ctx.bot.get_member(raw, ctx.guild_id)
        except NotFound:
            return None

    # case: str
    if isinstance(raw, str):
        # mention?
        mention = re.findall(r"^<?@?!?([0-9]{15,20})>?$", raw)
        if mention:
            try:
                return await ctx.bot.get_member(mention[0], ctx.guild_id)
            except NotFound:
                return None

        # name#discriminator?
        if len(raw) > 5 and raw[-5] == "#":
            name, _, discriminator = raw.rpartition("#")
            for member in ctx.guild.members:
                if member.user.username == name and member.user.discriminator == discriminator:
                    return member

        # name?
        for member in ctx.guild.members:
            if member.user.username == raw:
                return member

        # nick?
        for member in ctx.guild.members:
            if member.nickname == raw:
                return member

    return None
