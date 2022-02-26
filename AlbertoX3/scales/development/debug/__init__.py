__all__ = (
    "Debug",
    "setup",
)


from sqlalchemy import MetaData

from dis_snek.ext.debug_scale import DebugScale, debug_embed, InteractionContext  # noqa
from dis_snek.ext.paginators import Paginator
from dis_snek import (
    Snake,
    Scale,
    SlashCommandOption,
    SlashCommandChoice,
    OptionTypes,
)

from AlbertoX3.database import Base, db, select, db_wrapper


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

    @DebugScale.debug_info.subcommand(
        "database",
        options=[
            SlashCommandOption("table", OptionTypes.STRING),
            SlashCommandOption(
                "option",
                OptionTypes.STRING,
                choices=[
                    SlashCommandChoice("values", "values"),
                    SlashCommandChoice("schema", "schema"),
                ],
            ),
        ],
        sub_cmd_description="Get information about the database",
    )
    @db_wrapper
    async def database_info(self, ctx: InteractionContext) -> None:
        await ctx.defer()

        res = []
        for t in Base.__subclasses__():
            if t.__tablename__ == ctx.kwargs["table"]:
                if ctx.kwargs["option"] == "values":
                    for r in await db.exec(select(t.__table__)):
                        res.append(str(r))
                elif ctx.kwargs["option"] == "schema":
                    res.append(repr(t.__table__))
                else:
                    res.append(f"Unknown option {ctx.kwargs['option']!r}")
                break

        else:
            p = ", ".join(t.__tablename__ for t in Base.__subclasses__())
            res.append(f"Can't find table {ctx.kwargs['table']!r}")
            res.append(f"Possible tables are: {p}")

        await Paginator.create_from_string(
            self.bot, "\n".join(res or ["Empty!"]), "```", "```", 2000, 300
        ).send(ctx)


def setup(bot: Snake):
    Debug(bot)
