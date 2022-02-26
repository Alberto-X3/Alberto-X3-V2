__all__ = (
    "Kick",
    "setup",
)


from AlbertoX3.translations import t
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
from .models import DBKick


tg = t.g
t = t.kick


class Kick(Scale):
    @message_command()
    async def kick(self, ctx: Context, who: str, *reason: str):
        reason = " ".join(reason) or tg.no_reason
        who: Member = await get_member(ctx, who)
        embed = Embed(
            timestamp=Timestamp.now(),
            footer=EmbedFooter(
                text=tg.executed_by(user=ctx.author, id=ctx.author.id),
                icon_url=ctx.author.display_avatar.url,
            ),
        )

        if who is not None:
            await DBKick.add(who.id, ctx.author.id, reason)
            embed.description = t.kicked(user=who, reason=reason)
            embed.color = Colors.kicked
        else:
            embed.description = tg.not_found.user
            embed.color = Colors.failed

        await ctx.message.reply(embed=embed)


def setup(bot: Snake):
    Kick(bot)
