from AlbertUnruhUtils.utils.logger import get_logger
from pathlib import Path
from traceback import format_exception

from AlbertoX3 import (
    load_config_file,
    Config,
    get_config_values,
    AllColors,
    TOKEN,
)

from dis_snek import (
    Snake,
    ActivityType,
    Intents,
    Activity,
    Context,
    Embed,
    EmbedFooter,
    Timestamp,
    File,
)


get_logger("asyncio").setLevel("INFO")
logger = get_logger(None)


config_path = Path(__file__).parent.parent / "config.yml"
logger.debug(f"Loading Config from {config_path.absolute()}")
load_config_file(config_path)
logger.info(f"Config has now following values: \n{get_config_values()}")


bot = Snake(
    intents=Intents.ALL,
    default_prefix=Config.PREFIX,
    fetch_members=True,
    debug_scope=691620697335660554,
    asyncio_debug=True,
    activity=Activity.create(
        "Albert coding me",
        ActivityType.WATCHING,
        Config.REPO_LINK,
    ),
    sync_interactions=True,
    delete_unused_application_cmds=True,
)


bot.grow_scale("dis_snek.ext.debug_scale")


scale_import = (
    Config.SCALES_FOLDER_RAW.replace("/", ".").replace("\\", ".").removesuffix(".")
)
for category in Config.SCALES_FOLDER.iterdir():
    if category.is_file() or category.name.startswith("_"):
        continue
    for extension in category.iterdir():
        if extension.is_file() or extension.name.startswith("_"):
            continue
        logger.info(f"Adding Scale '{scale_import}.{category.name}.{extension.name}'")
        bot.grow_scale(
            f"{scale_import}.{category.name}.{extension.name}",
        )


async def on_command_error(ctx: Context, error: Exception, *args, **kwargs):
    await ctx.send(
        embed=Embed(
            color=AllColors.error,
            title="An internal error occurred :(",
            footer=EmbedFooter(
                icon_url=bot.user.avatar.url,
                text=Config.NAME,
            ),
            timestamp=Timestamp.now(),
        ),
    )
    to_ping = "".join(f"<@{c[0]}>" for c in Config.CONTRIBUTORS)
    f = Path(__file__).parent / f"tmp/{ctx.message.id}.log"
    f.write_text("".join(format_exception(error)), encoding="utf-8")  # type: ignore
    embed = Embed(
        description=f"**An error occurred [__here__]({ctx.message.jump_url}).**",
        color=AllColors.error,
    )
    embed.add_field("Guild", ctx.guild.name, True)
    embed.add_field("Channel", ctx.channel.mention, True)
    embed.add_field("User", ctx.author.mention, True)
    await (await bot.get_channel(945784138416418907)).send(
        content=f"||{to_ping}||",
        embed=embed,
        file=File(f, "traceback.py"),
    )
    await Snake.on_command_error(bot, ctx, error, *args, **kwargs)
    f.unlink()


bot.on_command_error = on_command_error


bot.start(TOKEN)
