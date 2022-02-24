__all__ = (
    "Kick",
    "setup",
)


from AlbertoX3.utils import get_member

from dis_snek import (
    Snake,
    Scale,
    Context,
    Member,
    message_command,
    Embed,
    Timestamp,
    EmbedFooter,
)

from .colors import Colors


class Kick(Scale):
    @message_command()
    async def kick(self, ctx: Context, who: str, *reason: str):
        reason = " ".join(reason) or "No reason"
        who: Member = await get_member(ctx, who)
        embed = Embed(
            timestamp=Timestamp.now(),
            footer=EmbedFooter(
                text=f"Executed by {ctx.author}", icon_url=ctx.author.display_avatar.url
            ),
        )

        if who is not None:
            embed.description = (
                f"You tried to kick `{who}` with following reason: `{reason}`"
            )
            embed.color = Colors.kicked
        else:
            embed.description = ":(\nI can't find this User..."
            embed.color = Colors.failed

        await ctx.message.reply(embed=embed)


def setup(bot: Snake):
    Kick(bot)
