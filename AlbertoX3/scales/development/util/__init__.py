from __future__ import annotations


__all__ = (
    "Util",
    "setup",
)


import inspect

from functools import partial
from typing import TYPE_CHECKING

from dis_snek.ext.paginators import Paginator
from dis_snek import message_command

from AlbertoX3.adis_snek import Scale


if TYPE_CHECKING:
    from dis_snek import Snake, MessageContext


class Util(Scale):
    @message_command("src")
    async def src(self, ctx: MessageContext):
        query = ctx.args[0] if ctx.args else None
        obj = None
        if obj is None:
            obj = self.bot.commands.get(query)
        if obj is None:
            obj = self.bot.scales.get(query)

        if hasattr(obj, "callback"):
            obj = obj.callback

        while isinstance(obj, partial):
            obj = obj.func

        if isinstance(obj, Scale):
            obj = obj.__class__

        assert obj is not None, f"Unable to find `{query}`!"

        paginator = Paginator.create_from_string(
            self.bot,
            inspect.getsource(obj).replace("`", "`\u200B"),
            "```py\n",
            "\n```",
            4000,
            120,
        )

        await paginator.send(ctx, True)


def setup(bot: Snake):
    Util(bot)
