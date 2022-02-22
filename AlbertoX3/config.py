__all__ = (
    "Contributor",
    "Config",
    "get_config_values",
    "load_config_file",
)


import re
from pathlib import Path
from yaml import safe_load

from .utils import get_values


class Contributor:
    """
    A collection of every contributor.

    Notes
    -----
    Values are ``("Discord ID", ("GitHub ID", "GitHub Node-ID"))``-tuples.
    Following signature is used: ``tuple[int, tuple[int, str]]``
    """

    AlbertUnruh = (546320163276849162, (73029826, "MDQ6VXNlcjczMDI5ODI2"))


class Config:
    """
    Global Configuration for the bot.

    Notes
    -----
    The values will be inserted and filled at runtime whenever
    ``AlbertoX3.config.load_*()`` is called.
    """

    # bot
    NAME: str
    VERSION: str
    PREFIX: str

    # repo
    REPO_OWNER: str
    REPO_NAME: str
    REPO_LINK: str
    REPO_ICON: str

    # help
    SUPPORT_DISCORD: str

    # developers
    AUTHOR: tuple[int, tuple[int, str]]
    CONTRIBUTORS: set[tuple[int, tuple[int, str]]]

    # language
    LANGUAGE_DEFAULT: str
    LANGUAGE_FALLBACK: str
    LANGUAGE_AVAILABLE: list[str]

    # scales
    SCALES_FOLDER_RAW: str
    SCALES_FOLDER: Path


def get_config_values() -> str:
    return get_values(Config)


def load_bot(config: dict):
    Config.NAME = config["name"]

    with open(Path(__file__).parent / "__init__.py", encoding="utf-8") as f:
        version = re.search(
            r"^__version__\s*=\s*[\'\"]([^\'\"]*)[\'\"]", f.read(), re.MULTILINE
        ).group(1)

    # append version identifier based on commit count
    try:
        import subprocess

        p = subprocess.Popen(
            ["git", "rev-list", "--count", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()
        if out:
            version += out.decode("utf-8").strip()

        p = subprocess.Popen(
            ["git", "rev-parse", "--short", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()
        if out:
            version += "+g" + out.decode("utf-8").strip()

    except Exception as e:
        from warnings import warn

        warn(
            message=f"\033[31mUnable to append version identifier!\033[0m "
            f"\033[35m{e.__class__.__name__}: {e}\033[0m",
            category=UserWarning,
        )

    Config.VERSION = version
    Config.PREFIX = config["prefix"]


def load_repo(config: dict):
    Config.REPO_OWNER = config["repo"]["owner"]
    Config.REPO_NAME = config["repo"]["name"]
    Config.REPO_LINK = f"https://github.com/{Config.REPO_OWNER}/{Config.REPO_NAME}"
    Config.REPO_ICON = config["repo"]["icon"]


def load_help(config: dict):
    Config.SUPPORT_DISCORD = config["discord"]


def load_developers(config: dict):
    Config.AUTHOR = getattr(Contributor, config["author"])
    Config.CONTRIBUTORS = {getattr(Contributor, c) for c in config["contributors"]}


def load_language(config: dict):
    Config.LANGUAGE_DEFAULT = config["language"]["default"]
    Config.LANGUAGE_FALLBACK = config["language"]["fallback"]
    Config.LANGUAGE_AVAILABLE = config["language"]["available"]


def load_scales(config: dict, path: Path = Path.cwd()):
    Config.SCALES_FOLDER_RAW = config["scale"]["folder"]
    folder = Path(Config.SCALES_FOLDER_RAW)
    if not folder.is_absolute():  # relative path is given
        folder = path / folder
    Config.SCALES_FOLDER = folder


def load_config_file(path: Path):
    """
    Loads the configuration.

    Parameters
    ----------
    path: Path
        The path to the config-file.
    """
    with path.open(encoding="utf-8") as f:
        config = safe_load(f)

    load_bot(config)
    load_repo(config)
    load_help(config)
    load_developers(config)
    load_language(config)
    load_scales(config, path.parent)
