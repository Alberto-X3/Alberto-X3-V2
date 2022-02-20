from AlbertoX3.utils import get_member

from dis_snek import Snake
from dis_snek.models import Scale, Context, Member
from dis_snek.models.command import message_command


class Kick(Scale):
    @message_command()
    async def kick(self, ctx: Context, who: str, *reason: str):
        reason = " ".join(reason) or "No reason"
        who: Member = await get_member(ctx, who)
        if who is None:
            await ctx.channel.send(":(\nI can't find this User...")
        else:
            await ctx.channel.send(
                f"You tried to kick `{who}` with following reason: `{reason}`"
            )


def setup(bot: Snake):
    Kick(bot)
