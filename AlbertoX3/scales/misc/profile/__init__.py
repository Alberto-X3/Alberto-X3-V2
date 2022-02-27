__all__ = (
    "Profile",
    "setup",
)


from asyncio import sleep
from pathlib import Path
from PIL import Image, ImageEnhance

from dis_snek import (
    Scale,
    Snake,
    message_command,
    MessageContext,
    Embed,
    EmbedFooter,
    EmbedAttachment,
    Timestamp,
    File,
)

from AlbertoX3.aio import run_in_thread
from AlbertoX3.translations import t
from AlbertoX3.utils import get_user

from .colors import Colors


tg = t.g
t = t.profile


def create_ukraine_flag():
    """
    Little helper-function.

    Returns
    -------
    Image.Image
        The Ukraine flag (4096x4096).
    """
    img = Image.new("RGB", (4096, 4096), (0, 91, 188, 100))
    img.paste(Image.new("RGB", (4096, 4096 // 2), (255, 214, 0, 100)), (0, 4096 // 2))
    img.save(Profile.pattern_folder / "ukraine.png")
    return img


class Profile(Scale):
    pattern_folder = Path(__file__).parent / "patterns"
    pattern_folder.mkdir(exist_ok=True)

    @message_command("profile")
    async def profile(self, ctx: MessageContext):
        args = ctx.args.copy()
        pattern = args.pop(0) if args else ""
        if not (negative := "negative" not in args):  # is weird, but works
            args.remove("negative")
        for i, arg in enumerate(args):
            if arg.startswith("user::"):
                if arg == "user::":
                    user = args.pop(i+1)
                    args.pop(i)
                else:
                    user = args.pop(i).removeprefix("user::")
                user = await get_user(ctx, user)
                break
        else:
            user = ctx.author
            user = getattr(user, "user", user)
        saturation_boost = args.pop(0) if args else "1"

        assert pattern in (
            available := list(
                map(
                    lambda p: p.name.removesuffix(".png"), self.pattern_folder.iterdir()
                )
            )
        ), t.invalid_pattern(available=", ".join(available), given=pattern)
        assert (
            saturation_boost.removeprefix("-").replace(".", "").isnumeric()
            and saturation_boost.count(".") <= 1
            and -100 <= (saturation_boost := float(saturation_boost)) <= 100
        ), t.invalid_saturation_boost
        assert user is not None, tg.not_found.user

        embed_data = Embed(
            timestamp=Timestamp.now(),
            footer=EmbedFooter(
                text=tg.executed_by(user=ctx.author, id=ctx.author.id),
                icon_url=ctx.author.display_avatar.url,
            ),
            color=Colors.created,
        ).to_dict()

        # download
        msg = await ctx.reply(
            embed=Embed(description=t.progress.downloading, **embed_data)
        )
        await sleep(0.3)  # ratelimits...
        f = Path(__file__).parent / f"tmp/{ctx.author.id}-{pattern}.png"
        await user.avatar.save(f, size=4096)

        # prepare profile
        await msg.edit(
            embed=Embed(description=t.progress.preparing.profile, **embed_data)
        )
        await sleep(0.3)  # ratelimits...
        img: Image.Image = await run_in_thread(Image.open, f)
        img = await run_in_thread(img.convert, "L")
        img = await run_in_thread(img.resize, (4096, 4096))

        # prepare pattern
        await msg.edit(
            embed=Embed(
                description=t.progress.preparing.pattern(pattern=pattern), **embed_data
            )
        )
        await sleep(0.3)  # ratelimits...
        img_p: Image.Image = await run_in_thread(
            Image.open, self.pattern_folder / f"{pattern}.png"
        )
        img_p = await run_in_thread(img_p.resize, (4096, 4096))

        # create result
        await msg.edit(embed=Embed(description=t.progress.creating, **embed_data))
        await sleep(0.3)  # ratelimits...
        img_p = await run_in_thread(
            Image.composite,
            Image.new("RGBA", (4096, 4096), (255 * negative,) * 4),
            img_p,
            img,
        )
        img_p = await run_in_thread(ImageEnhance.Color(img_p).enhance, saturation_boost)

        # send result
        img_p.save(f)
        await msg.edit(
            file=File(f, f"{pattern}.png"),
            embed=Embed(
                description=t.new_picture,
                image=EmbedAttachment(f"attachment://{pattern}.png"),
                **embed_data,
            ),
        )
        f.unlink()

    @profile.error
    async def profile_error(self, e: Exception, ctx: MessageContext, *_):
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
    Profile(bot)
