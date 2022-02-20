__all__ = (
    "get_member",
    "get_user",
)


import re

from dis_snek import Context, User, Member


async def get_member(
    ctx: Context,
    raw: str | int | User | Member,
) -> Member | None:
    match raw:
        case Member():
            return raw
        case User():
            return await ctx.bot.get_member(raw.id, ctx.guild_id)
        case int() | _ if str(raw).isnumeric():
            return await ctx.bot.get_member(raw, ctx.guild_id)
        case str():
            # mention?
            mention = re.findall(r"^<?@?!?([0-9]{15,20})>?$", raw)
            if mention:
                return await ctx.bot.get_member(mention[0], ctx.guild_id)

            # name#discriminator?
            if len(raw) > 5 and raw[-5] == "#":
                name, _, discriminator = raw.rpartition("#")
                for member in ctx.guild.members:
                    # correct name?
                    if member.user.username == name:
                        # only discriminator left to check
                        if member.user.discriminator == discriminator:
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


async def get_user(
    ctx: Context,
    raw: str | int | User | Member,
) -> User | None:
    match raw:
        case Member():
            return raw.user
        case User():
            return raw
        case int() | _ if str(raw).isnumeric():
            return await ctx.bot.get_user(raw)
        case str():
            # mention?
            mention = re.findall(r"^<?@?!?([0-9]{15,20})>?$", raw)
            if mention:
                return await ctx.bot.get_user(mention[0])

            # name#discriminator?
            if len(raw) > 5 and raw[-5] == "#":
                name, _, discriminator = raw.rpartition("#")
                for user in ctx.bot.cache.user_cache.values():
                    # correct name?
                    if user.username == name:
                        # only discriminator left to check
                        if user.discriminator == discriminator:
                            return user

            # name?
            for user in ctx.bot.cache.user_cache.values():
                if user.username == raw:
                    return user

            # nick?
            for member in ctx.guild.members:
                if member.nickname == raw:
                    return member.user

            return None
