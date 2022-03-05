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

from .colors import Colors
from .models import ItemModel, InventoryModel


tg = t.g
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

    @inventory.error
    @item.error
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
    for id in items:  # noqa
        if await ItemModel.get(id) is None:
            await ItemModel.add(id, **items[id])


def setup(bot: Snake):
    Inventory(bot)
    bot.loop.run_until_complete(
        create_all_items(safe_load((Path(__file__).parent / "items.yml").read_text()))
    )
