from dotenv import load_dotenv
from os import environ
from pathlib import Path

from AlbertoX3 import (
    load_config_file,
    Config,
)

from dis_snek import Snake, ActivityType, Intents, Activity


load_dotenv()


config_path = Path(__file__).parent.parent / "config.yml"
load_config_file(config_path)


bot = Snake(
    intents=Intents.ALL,
    default_prefix=Config.PREFIX,
    fetch_members=True,
    debug_scope=True,
    asyncio_debug=True,
    activity=Activity.create(
        "Albert coding me",
        ActivityType.WATCHING,
        Config.REPO_LINK,
    ),
)


for category in Config.EXTENSION_FOLDER.iterdir():
    if category.is_file() or category.name.startswith("_"):
        continue
    for extension in category.iterdir():
        if extension.is_file() or extension.name.startswith("_"):
            continue
        bot.grow_scale(
            file_name=f"{Config.EXTENSION_FOLDER.name}.{category.name}.{extension.name}",
            package="AlbertoX3",
        )


bot.start(environ["TOKEN"])
