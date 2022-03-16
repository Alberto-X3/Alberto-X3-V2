from __future__ import annotations


__all__ = (
    "Util",
    "setup",
)


import inspect

from typing import TYPE_CHECKING

from dis_snek import message_command

from AlbertoX3.adis_snek import Scale


if TYPE_CHECKING:
    from dis_snek import Snake, MessageContext


class Util(Scale):
    @message_command("src")
    async def src(self, ctx: MessageContext):
        raise NotImplementedError("This isn't implemented yet!")


def setup(bot: Snake):
    Util(bot)
