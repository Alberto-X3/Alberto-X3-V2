__all__ = (
    "get_values",
    "get_member",
    "get_user",
)


import re

from dis_snek import Context, User, Member


def get_values(obj: ...) -> str:
    keys: list[str] = [k for k in dir(obj) if not k.startswith("_")]
    length = len(max(keys, key=len))
    string: list[str] = []

    for key in keys:
        val = getattr(obj, key)
        string.append(f"`{key.ljust(length)}`: {val!r}")

    return "\n".join(string)


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

            # lowercase?
            if raw.islower():
                # name#discriminator? (lowercase)
                if len(raw) > 5 and raw[-5] == "#":
                    name, _, discriminator = raw.rpartition("#")
                    for member in ctx.guild.members:
                        # correct name? (lowercase)
                        if member.user.username.lower() == name:
                            # only discriminator left to check
                            if member.user.discriminator == discriminator:
                                return member

                # name? (lowercase)
                for member in ctx.guild.members:
                    if member.user.username.lower() == raw:
                        return member

                # nick? (lowercase)
                for member in ctx.guild.members:
                    if member.nickname.lower() == raw:
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

            # lowercase?
            if raw.islower():
                # name#discriminator? (lowercase)
                if len(raw) > 5 and raw[-5] == "#":
                    name, _, discriminator = raw.rpartition("#")
                    for user in ctx.bot.cache.user_cache.values():
                        # correct name? (lowercase)
                        if user.username.lower() == name:
                            # only discriminator left to check
                            if user.discriminator == discriminator:
                                return user

                # name? (lowercase)
                for user in ctx.bot.cache.user_cache.values():
                    if user.username.lower() == raw:
                        return user

                # nick? (lowercase)
                for member in ctx.guild.members:
                    if member.nickname.lower() == raw:
                        return member.user

            return None
