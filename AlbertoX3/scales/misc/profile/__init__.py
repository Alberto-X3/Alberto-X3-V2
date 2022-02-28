__all__ = (
    "Profile",
    "setup",
)


from AlbertUnruhUtils.utils.logger import get_logger
from asyncio import sleep
from itertools import count
from pathlib import Path
from PIL import Image

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

count = count()
logger = get_logger(__name__.split(".")[-1], level=None, add_handler=False)


def create_ukraine_flag():
    """
    Little helper-function.

    Returns
    -------
    Image.Image
        The Ukraine flag (4096x4096).
    """
    img = Image.new("RGBA", (4096, 4096), (0, 0, 0, 0))
    rows = [
        (0, 91, 188),
        (255, 214, 0),
    ]
    payload = "RGBA", (4096, 4096 // len(rows))
    for i, row in enumerate(rows):
        img.paste(Image.new(*payload, row + (255,)), (0, 4096 // len(rows) * i))  # type: ignore
    img.save(Profile.pattern_folder / "ukraine.png")
    return img


def create_rainbow_flag():
    """
    Little helper-function.

    Returns
    -------
    Image.Image
        The Rainbow flag (4096x4096).
    """
    img = Image.new("RGBA", (4096, 4096), (0, 0, 0, 0))
    rows = [
        (228, 3, 3),
        (255, 140, 0),
        (255, 237, 0),
        (0, 128, 38),
        (0, 77, 255),
        (117, 7, 135),
    ]
    payload = "RGBA", (4096, 4096 // len(rows))
    for i, row in enumerate(rows):
        img.paste(Image.new(*payload, row + (255,)), (0, 4096 // len(rows) * i))  # type: ignore
    img.save(Profile.pattern_folder / "rainbow.png")
    return img


def create_all_flags():
    """
    Creates every flag.
    """
    import re

    flag_creator = re.compile(r"^create_([a-z]+)_flag$")

    for name, func in globals().items():
        if callable(func):
            if match := flag_creator.search(name):
                logger.debug(f"Creating flag {match.group(1)}")
                func()


class Profile(Scale):
    pattern_folder = Path(__file__).parent / "patterns"
    pattern_folder.mkdir(exist_ok=True)

    @message_command("profile")
    async def profile(self, ctx: MessageContext):
        args = ctx.args.copy()
        pattern = args.pop(0) if args else ""
        for i, arg in enumerate(args):
            if arg.startswith("user::"):
                if arg == "user::":
                    user = args.pop(i + 1)
                    args.pop(i)
                else:
                    user = args.pop(i).removeprefix("user::")
                user = await get_user(ctx, user)
                break
        else:
            user = ctx.author
            user = getattr(user, "user", user)
        opacity = args.pop(0) if args else "50"

        assert pattern in (
            available := list(
                map(
                    lambda p: p.name.removesuffix(".png"), self.pattern_folder.iterdir()
                )
            )
        ), t.invalid_pattern(available=", ".join(available), given=pattern)
        assert (
            opacity.removeprefix("-").replace(".", "").isnumeric()
            and opacity.count(".") <= 1
            and 0 <= (opacity := float(opacity)) <= 100
        ), t.invalid_opacity
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
        await sleep(0.4)  # ratelimits...
        f = Path(__file__).parent / f"tmp/{next(count)}.png"
        await user.avatar.save(f, size=4096)

        # prepare profile
        await msg.edit(
            embed=Embed(description=t.progress.preparing.profile, **embed_data)
        )
        await sleep(0.4)  # ratelimits...
        img: Image.Image = await run_in_thread(Image.open, f)
        img = await run_in_thread(img.convert, "LA")
        img = await run_in_thread(img.convert, "RGBA")
        img = await run_in_thread(img.resize, (4096, 4096))

        # prepare pattern
        await msg.edit(
            embed=Embed(
                description=t.progress.preparing.pattern(pattern=pattern), **embed_data
            )
        )
        await sleep(0.4)  # ratelimits...
        img_p: Image.Image = await run_in_thread(
            Image.open, self.pattern_folder / f"{pattern}.png"
        )
        img_p = await run_in_thread(img_p.resize, (4096, 4096))

        # create result
        await msg.edit(embed=Embed(description=t.progress.creating, **embed_data))
        await sleep(0.4)  # ratelimits...
        img = await run_in_thread(Image.blend, img, img_p, opacity / 100)

        # send result
        img.save(f)
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
    create_all_flags()
