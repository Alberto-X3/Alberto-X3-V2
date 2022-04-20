from __future__ import annotations


__all__ = (
    "get_values",
    "get_member",
    "get_user",
    "get_bool",
    "get_subclasses_in_scales",
    "get_language",
)


import re
import sys

from typing import TYPE_CHECKING, TypeVar, Type
from dis_snek import Context, User, Member, Snowflake_Type

from .types import PrimitiveScale


if TYPE_CHECKING:
    from typing import List, Optional, Any


T = TypeVar("T")


def get_values(obj: object) -> str:
    keys: List[str] = [k for k in dir(obj) if not k.startswith("_")]
    length: int = len(max(keys, key=len))
    string: List[str] = []

    for key in keys:
        val = getattr(obj, key)
        string.append(f"`{key.ljust(length)}`: {val!r}")

    return "\n".join(string)


async def get_member(
    ctx: Context,
    raw: str | int | User | Member,
) -> Optional[Member]:
    match raw:
        case Member():
            return raw
        case User():
            return await ctx.bot.fetch_member(raw.id, ctx.guild_id)
        case int() | _ if str(raw).isnumeric():
            return await ctx.bot.fetch_member(raw, ctx.guild_id)
        case str():
            # mention?
            mention = re.findall(r"^<?@?!?(\d{15,20})>?$", raw)
            if mention:
                return await ctx.bot.fetch_member(mention[0], ctx.guild_id)

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
                    if member.nickname is None:
                        continue
                    if member.nickname.lower() == raw:
                        return member

            return None


async def get_user(
    ctx: Context,
    raw: str | int | User | Member,
) -> Optional[User]:
    match raw:
        case Member():
            return raw.user
        case User():
            return raw
        case int() | _ if str(raw).isnumeric():
            return await ctx.bot.fetch_user(raw)
        case str():
            # mention?
            mention = re.findall(r"^<?@?!?(\d{15,20})>?$", raw)
            if mention:
                return await ctx.bot.fetch_user(mention[0])

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
                    if member.nickname is None:
                        continue
                    if member.nickname.lower() == raw:
                        return member.user

            return None


def get_bool(
    raw: Any,
    /,
) -> bool:
    """
    Parameters
    ----------
    raw: Any
        The input to get the boolean from.

    Returns
    -------
    bool

    Raises
    ------
    ValueError
        If it's unclear what the boolean is.
    """
    if raw in ["True", "true", "t", "yes", "y", "1", 1, True]:
        return True
    if raw in ["False", "false", "f", "no", "n", "0", 0, False]:
        return False
    raise ValueError(f"Cannot assign {raw!r} to True or False!")


def get_subclasses_in_scales(
    base: Type[T],
    *,
    scales: List[PrimitiveScale] = None,
) -> List[Type[T]]:
    """
    Returns all subclasses from base declared in

    Parameters
    ----------
    base: Type[T]
        The baseclass to get the subclasses from.
    scales: List[PrimitiveScale], optional
        The scales to look at (defaults to ``Config.SCALES``).

    Returns
    -------
    List[Type[T]]
    """
    if scales is None:
        from .config import Config

        scales = Config.SCALES

    scales = set([scale.package for scale in scales])
    return [
        cls
        for cls in base.__subclasses__()
        if sys.modules[cls.__module__].__package__ in scales
    ]


def get_language(
    *,
    guild: Snowflake_Type = None,
    user: Snowflake_Type = None,
) -> str | None:
    assert not (
        guild is not None and user is not None
    ), "Can't have both 'guild' and 'user' set!"
    # ToDo: connect to database
    return None
