from AlbertUnruhUtils.utils.logger import get_logger
from dotenv import load_dotenv
from os import environ
from pathlib import Path

from AlbertoX3 import (
    load_config_file,
    Config,
    get_config_values,
)

from dis_snek import Snake, ActivityType, Intents, Activity


load_dotenv()
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


for category in Config.EXTENSION_FOLDER.iterdir():
    if category.is_file() or category.name.startswith("_"):
        continue
    for extension in category.iterdir():
        if extension.is_file() or extension.name.startswith("_"):
            continue
        logger.info(f"Adding Scale '{category.name}.{extension.name}'")
        bot.grow_scale(
            f"AlbertoX3.{Config.EXTENSION_FOLDER.name}.{category.name}.{extension.name}",
        )


bot.start(environ["TOKEN"])
