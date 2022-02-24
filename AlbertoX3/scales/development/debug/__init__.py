__all__ = (
    "Debug",
    "setup",
)


from dis_snek.ext.debug_scale import DebugScale, debug_embed, InteractionContext  # noqa
from dis_snek import (
    Snake,
    Scale,
)


class Debug(DebugScale, Scale):
    @DebugScale.debug_info.subcommand(
        "config", sub_cmd_description="Get information about the config"
    )
    async def config_info(self, ctx: InteractionContext) -> None:
        await ctx.defer()
        e = debug_embed("Config")

        from AlbertoX3.config import get_config_values

        e.description = get_config_values()
        await ctx.send(embeds=[e])


def setup(bot: Snake):
    Debug(bot)
