__all__ = (
    "Money",
    "setup",
)


from dis_snek import (
    Snake,
    message_command,
    MessageContext,
    Embed,
    EmbedFooter,
    Timestamp,
)

from AlbertoX3.adis_snek import Scale
from AlbertoX3.database import db, filter_by
from AlbertoX3.translations import t
from AlbertoX3.utils import get_user

from .colors import Colors
from .models import MoneyModel


tg = t.g
t = t.money


async def get_global_money() -> int:
    return sum(map(lambda m: m.amount, await db.all(filter_by(MoneyModel))))


async def get_emoji(amount: int, global_amount: int | None = None) -> str:
    global_amount = global_amount or await get_global_money()
    if global_amount / 1 <= amount:
        return "\uD83D\uDCB0"  # :moneybag:
    if global_amount / 2 <= amount:
        return "\uD83D\uDCB4"  # :yen:
    if global_amount / 4 <= amount:
        return "\uD83D\uDCB7"  # :pound:
    if global_amount / 8 <= amount:
        return "\uD83D\uDCB6"  # :euro:
    return "\uD83D\uDCB5"  # :dollar:


class Money(Scale):
    @message_command("money")
    async def money(self, ctx: MessageContext):
        amount = (await MoneyModel.get(ctx.author.id)).amount
        amount_g = await get_global_money()

        embed = Embed(
            timestamp=Timestamp.now(),
            footer=EmbedFooter(
                text=tg.executed_by(user=ctx.author, id=ctx.author.id),
                icon_url=ctx.author.display_avatar.url,
            ),
            color=Colors.money,
        )
        embed.add_field(
            t.you.title,
            t.you.money(cnt=amount, emoji=await get_emoji(amount, amount_g))
            + "\n"
            + t.percentage_from.market(cnt=amount / amount_g * 100),
        )
        embed.add_field(
            t.all.title,
            t.all.money(cnt=amount_g, emoji=await get_emoji(amount_g, amount_g)),
        )

        await ctx.reply(
            embed=embed,
        )

    @message_command("pay")
    async def pay(self, ctx: MessageContext):
        args = ctx.args.copy()
        user = await get_user(ctx, args.pop(0) if args else "")
        assert user is not None, tg.not_found.user
        amount = args.pop(0) if args else "0"
        assert amount.removeprefix("-").isnumeric(), t.amount.must_be_numeric
        assert (amount := int(amount)) > 0, t.amount.must_be_positive
        payer = await MoneyModel.get(ctx.author.id)
        emoji = await get_emoji(amount, (g := await get_global_money()))
        assert payer.amount >= amount, t.to_expensive(
            required=amount,
            available=payer.amount,
            emoji_r=emoji,
            emoji_a=await get_emoji(payer.amount, g),
        )

        await MoneyModel.update(user.id, amount, True)
        await MoneyModel.update(payer.user, -amount, True)

        await ctx.reply(
            embed=Embed(
                description=t.transaction(
                    amount=amount, receiver=user.mention, emoji=emoji
                ),
                timestamp=Timestamp.now(),
                footer=EmbedFooter(
                    text=tg.executed_by(user=ctx.author, id=ctx.author.id),
                    icon_url=ctx.author.display_avatar.url,
                ),
                color=Colors.transaction,
            ),
        )

    @money.error
    @pay.error
    async def error(self, e: Exception, ctx: MessageContext, *_):
        if isinstance(e, AssertionError):
            return await ctx.reply(
                embed=Embed(
                    description=e.args[0],
                    timestamp=Timestamp.now(),
                    footer=EmbedFooter(
                        text=tg.executed_by(user=ctx.author, id=ctx.author.id),
                        icon_url=ctx.author.display_avatar.url,
                    ),
                    color=Colors.assertion,
                ),
            )
        else:
            raise


def setup(bot: Snake):
    Money(bot)
