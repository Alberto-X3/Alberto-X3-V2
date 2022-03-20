from __future__ import annotations


__all__ = (
    "Contributor",
    "Config",
    "get_config_values",
    "get_scales",
    "load_config_file",
)


import re

from pathlib import Path
from typing import TYPE_CHECKING
from yaml import safe_load

from .contributor import Contributor
from .types import PrimitiveScale, FormatStr
from .utils import get_values, get_bool


if TYPE_CHECKING:
    from typing import Set, NoReturn, Dict, List


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
    AUTHOR: Contributor
    CONTRIBUTORS: Set[Contributor]

    # language
    LANGUAGE_DEFAULT: str
    LANGUAGE_FALLBACK: str
    LANGUAGE_AVAILABLE: List[str]

    # scales
    SCALES_FOLDER_RAW: str
    SCALES_FOLDER: Path
    SCALES: Set[PrimitiveScale]

    TMP_FOLDER_RAW: str
    TMP_FOLDER: Path
    TMP_PATTERN: FormatStr
    TMP_REMOVE: bool


def get_config_values() -> str:
    return get_values(Config)


def load_bot(config: Dict) -> NoReturn:
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


def load_repo(config: Dict) -> NoReturn:
    Config.REPO_OWNER = config["repo"]["owner"]
    Config.REPO_NAME = config["repo"]["name"]
    Config.REPO_LINK = f"https://github.com/{Config.REPO_OWNER}/{Config.REPO_NAME}"
    Config.REPO_ICON = config["repo"]["icon"]


def load_help(config: Dict) -> NoReturn:
    Config.SUPPORT_DISCORD = config["discord"]


def load_developers(config: Dict) -> NoReturn:
    Config.AUTHOR = getattr(Contributor, config["author"])
    Config.CONTRIBUTORS = set(
        map(lambda c: getattr(Contributor, c), config["contributors"])
    )


def load_language(config: Dict) -> NoReturn:
    Config.LANGUAGE_DEFAULT = config["language"]["default"]
    Config.LANGUAGE_FALLBACK = config["language"]["fallback"]
    Config.LANGUAGE_AVAILABLE = config["language"]["available"]


def load_scales(config: Dict, path: Path = Path.cwd()) -> NoReturn:
    Config.SCALES_FOLDER_RAW = config["scale"]["folder"]
    folder = Path(Config.SCALES_FOLDER_RAW)
    if not folder.is_absolute():  # a relative path is given
        folder = path / folder
    Config.SCALES_FOLDER = folder
    Config.SCALES = get_scales()


def get_scales(
    scale_marker: str = "__init__.py", *, cur_path: Path = None, cur_mod: str = ""
) -> Set[PrimitiveScale]:
    """
    Recursively gets every scale.

    Parameters
    ----------
    scale_marker: str
        The filename to recognize a Scale.
    cur_path: Path, optional
        The current path (needed due to recursion).
    cur_mod: str
        The current module (needed due to recursion).

    Returns
    -------
    Set[PrimitiveScale]
        All paths to the scales.
    """
    scales = set()

    cur_path = cur_path or Config.SCALES_FOLDER
    cur_mod = cur_mod or (
        Config.SCALES_FOLDER_RAW.replace("/", ".").replace("\\", ".").removesuffix(".")
    )

    for folder in cur_path.iterdir():
        if folder.is_file():
            if folder.name == scale_marker:
                scales.add(
                    PrimitiveScale(
                        name=folder.parent.name, package=cur_mod, path=folder.parent
                    )
                )
            continue

        if folder.name.startswith("_"):
            continue

        scales.update(get_scales(cur_path=folder, cur_mod=f"{cur_mod}.{folder.name}"))

    return scales


def load_tmp(config: Dict, path: Path = Path.cwd()) -> NoReturn:
    Config.TMP_FOLDER_RAW = config["tmp"]["folder"]
    folder = Path(Config.TMP_FOLDER_RAW)
    if not folder.is_absolute():  # a relative path is given
        folder = path / folder
    folder.mkdir(exist_ok=True)
    Config.TMP_FOLDER = folder
    Config.TMP_PATTERN = FormatStr(config["tmp"]["pattern"])
    Config.TMP_REMOVE = get_bool(config["tmp"]["remove"])


def load_config_file(path: Path) -> NoReturn:
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
    load_tmp(config, path.parent)
