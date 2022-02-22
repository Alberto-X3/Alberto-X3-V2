from AlbertoX3.colors import AllColors
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


class Kick(Scale):
    @message_command()
    async def kick(self, ctx: Context, who: Member, *reason: str):
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
            embed.color = AllColors.default
        else:
            embed.description = ":(\nI can't find this User..."
            embed.color = AllColors.error

        await ctx.message.reply(embed=embed)


def setup(bot: Snake):
    Kick(bot)
