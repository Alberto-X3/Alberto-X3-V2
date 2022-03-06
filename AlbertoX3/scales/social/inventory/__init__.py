__all__ = (
    "Inventory",
    "setup",
)


from pathlib import Path
from yaml import safe_load

from dis_snek import (
    Scale,
    Snake,
    message_command,
    MessageContext,
    Embed,
    EmbedFooter,
    Timestamp,
)

from AlbertoX3.translations import t
from AlbertoX3.scales.social.money import (
    Colors as mColors,
    MoneyModel,
    get_emoji,
    get_global_money,
)  # noqa

from .colors import Colors
from .models import ItemModel, InventoryModel


tg = t.g
tm = t.money
t = t.inventory


class Inventory(Scale):
    @message_command("item")
    async def item(self, ctx: MessageContext):
        item = ctx.args[0] if ctx.args else None
        assert item in t.items, t.item.not_found(item=item)
        item: ItemModel = await ItemModel.get(int(item))  # type: ignore

        t_item = getattr(t.items, str(item.id))
        name = t_item.name
        description = t_item.description

        info = [t.item.description(description=description)]
        if item.max_available is not None:
            info.append(t.item.quantity(cnt=item.max_available))
        info = "\n\n".join(info)

        embed = Embed(
            timestamp=Timestamp.now(),
            footer=EmbedFooter(
                text=tg.executed_by(user=ctx.author, id=ctx.author.id),
                icon_url=ctx.author.display_avatar.url,
            ),
            color=Colors.inventory,
        )
        embed.add_field(name, info)

        await ctx.reply(
            embed=embed,
        )

    @message_command("inventory")
    async def inventory(self, ctx: MessageContext):
        inventory = await InventoryModel.get(ctx.author.id)
        embed = Embed(
            description=t.inventory,
            timestamp=Timestamp.now(),
            footer=EmbedFooter(
                text=tg.executed_by(user=ctx.author, id=ctx.author.id),
                icon_url=ctx.author.display_avatar.url,
            ),
            color=Colors.inventory,
        )

        for inv in sorted(inventory, key=lambda i: i.item):
            if inv.quantity:
                t_item = getattr(t.items, str(inv.item))
                embed.add_field(
                    f"{t.item.id(id=inv.item)} | {t.item.name(name=t_item.name)}",
                    f"{t.item.quantity(cnt=inv.quantity)}",
                )

        if not embed.fields:
            embed.add_field(
                f"{t.item.id(id='/')} | {t.item.name(name='/')}",
                f"{t.item.description(description='/')}",
            )

        await ctx.reply(
            embed=embed,
        )

    @message_command("buy")
    async def buy(self, ctx: MessageContext):
        item = ctx.args[0] if ctx.args else ""
        assert item.isnumeric(), t.item.not_found(item=item)
        item = await ItemModel.get(int(item))
        assert item is not None, t.item.not_found(item=item.id)
        assert item.buyable, t.item.unbuyable(item=item.id)

        payer = await MoneyModel.get(ctx.author.id)
        emoji = await get_emoji(item.price, (g := await get_global_money()))
        assert payer.amount >= item.price, tm.to_expensive(
            required=item.price,
            available=payer.amount,
            emoji_r=emoji,
            emoji_a=await get_emoji(payer.amount, g),
        )
        if item.max_available is not None:
            assert (
                await item.get_claimed_amount() < item.max_available
            ), t.item.not_available(item=item.id)

        await MoneyModel.update(payer.user, -item.price, True)
        await InventoryModel.update(payer.user, item.id, 1, True)

        embed = Embed(
            description=t.bought(price=item.price, emoji=emoji, item=item.id),
            timestamp=Timestamp.now(),
            footer=EmbedFooter(
                text=tg.executed_by(user=ctx.author, id=ctx.author.id),
                icon_url=ctx.author.display_avatar.url,
            ),
            color=mColors.transaction,
        )

        t_item = getattr(t.items, str(item.id))
        description = t_item.description
        info = [t.item.description(description=description)]
        if item.max_available is not None:
            info.append(t.item.quantity(cnt=item.max_available))
        info = "\n\n".join(info)

        embed.add_field(t_item.name, info)

        await ctx.reply(
            embed=embed,
        )

    @item.error
    @inventory.error
    @buy.error
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


async def create_all_items(items):
    await __import__("asyncio").sleep(2)  # all tables should be created
    for id in items:  # noqa
        if await ItemModel.get(id) is None:
            await ItemModel.add(id, **items[id])


def setup(bot: Snake):
    Inventory(bot)
    bot.loop.create_task(
        create_all_items(safe_load((Path(__file__).parent / "items.yml").read_text()))
    )
