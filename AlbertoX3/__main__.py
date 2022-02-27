from AlbertUnruhUtils.utils.logger import get_logger
from itertools import count
from pathlib import Path
from traceback import format_exception

from AlbertoX3 import (
    load_config_file,
    Config,
    get_config_values,
    AllColors,
    TOKEN,
    db,
    load_translations,
    t,
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


logger = get_logger(None)
count = count()


config_path = Path(__file__).parent.parent / "config.yml"
logger.debug(f"Loading Config from {config_path.absolute()}")
load_config_file(config_path)
logger.info(f"Config has now following values: \n{get_config_values()}")

load_translations()


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


for scale in Config.SCALES:
    logger.info(f"Adding Scale '{scale.name}' from '{scale.package}'")
    bot.grow_scale(scale.package)


async def on_command_error(ctx: Context, error: Exception, *args, **kwargs):
    msg = await ctx.send(
        embed=Embed(
            color=AllColors.error,
            title=t.g.internal_error,
            footer=EmbedFooter(
                icon_url=bot.user.avatar.url,
                text=Config.NAME,
            ),
            timestamp=Timestamp.now(),
        ),
    )
    to_ping = "".join(f"<@{c[0]}>" for c in Config.CONTRIBUTORS)
    f = Path(__file__).parent / f"tmp/{next(count)}.log"
    f.parent.mkdir(exist_ok=True)
    f.write_text("".join(format_exception(error)), encoding="utf-8")  # type: ignore
    embed = Embed(
        description=f"**An error occurred [here]({msg.jump_url}).**",
        color=AllColors.error,
    )
    embed.add_field("Guild", ctx.guild.name, True)
    embed.add_field("Channel", ctx.channel.mention, True)
    embed.add_field("User", ctx.author.mention, True)
    await (await bot.fetch_channel(945784138416418907)).send(
        content=f"||{to_ping}||",
        embed=embed,
        file=File(f, "traceback.py"),
    )
    await Snake.on_command_error(bot, ctx, error, *args, **kwargs)
    f.unlink()


bot.on_command_error = on_command_error


bot.loop.run_until_complete(db.create_tables())
bot.start(TOKEN)
