from __future__ import annotations


__all__ = (
    "Translations",
    "merge",
    "load_translations",
    "t",
)


from AlbertUnruhUtils.utils.logger import get_logger
from pathlib import Path
from typing import TYPE_CHECKING
from yaml import safe_load

from .config import Config
from .types import PrimitiveScale
from .utils import get_language


if TYPE_CHECKING:
    from typing import Dict, List, Optional, NoReturn, Any


logger = get_logger(__name__.split(".")[-1], level=None, add_handler=False)


def merge(
    base: Dict,
    src: Dict,
) -> Dict:
    """
    Merges to dictionaries recursively.

    Parameters
    ----------
    base: Dict
        The dictionary to merge into.
    src: Dict
        The dictionary to merge into ``base``.

    Returns
    -------
    Dict
        The merged dictionary.
    """
    for k, v in src.items():
        if k in base and isinstance(v, dict) and isinstance(base[k], dict):
            merge(base[k], v)
        else:
            base[k] = v

    return base


class FormatStr(str):
    __call__ = str.format


class TranslationDict(dict):
    _fallback: Dict

    def __call__(self, *args, **kwargs):
        cnt = kwargs.get("cnt", kwargs.get("count", None))

        translation: str
        if cnt == 1:
            translation = self.one
        elif cnt == 0 and "zero" in self:  # optional
            translation = self.zero
        else:
            translation = self.many

        return translation.format(*args, **kwargs)

    def __getattr__(self, item: str):
        value = self.get(item, self._fallback[item])

        if isinstance(value, str):
            value = FormatStr(value)
        elif isinstance(value, dict):
            value = TranslationDict(value)
            value._fallback = self._fallback[item]

        return value

    def __contains__(self, item) -> bool:
        return super().__contains__(item) or self._fallback.__contains__(item)


class TranslationNamespace:
    _sources: List[Path]
    _translations: Dict[str, Dict[str, Any]]

    def __init__(self):
        self._sources = []
        self._translations = {}

    def tn_add_source(self, source: Path) -> NoReturn:
        self._sources.append(source)
        self._translations.clear()

    def tn_get_language(self, lan: str) -> Dict[str, Any]:
        assert lan in Config.LANGUAGE_AVAILABLE, (
            f"Unsupported language {lan!r}! "
            f"Supported languages are: {', '.join(Config.LANGUAGE_AVAILABLE)}"
        )

        if lan not in self._translations:
            logger.debug(f"Creating translations for {lan!r}")
            self._translations[lan] = {}
            for source in self._sources:
                if not (path := source / f"{lan}.yml".lower()).exists():
                    continue
                with path.open() as file:
                    merge(self._translations[lan], safe_load(file) or {})

        return self._translations[lan]

    def tn_get_translation(self, key: str):
        translations = self.tn_get_language(get_language() or Config.LANGUAGE_DEFAULT)
        if key not in translations:
            translations = self.tn_get_language(Config.LANGUAGE_FALLBACK)

        return translations[key]

    def __getattr__(self, item: str):
        value = self.tn_get_translation(item)

        if isinstance(value, str):
            value = FormatStr(value)
        elif isinstance(value, dict):
            value = TranslationDict(value)
            value._fallback = self.tn_get_language(Config.LANGUAGE_FALLBACK)[item]

        return value


class Translations:
    FALLBACK: str = "EN"
    _namespace: Dict[str, TranslationNamespace]

    def __init__(self):
        self._namespace = {}

    def register_translation_namespace(self, name: str, file: Path) -> NoReturn:
        if name not in self._namespace:
            logger.debug(f"Creating TranslationNamespace for {name!r}")
            self._namespace[name] = TranslationNamespace()
        else:
            logger.debug(f"Extending TranslationNamespace for {name!r}")

        self._namespace[name].tn_add_source(file)

    def __getattr__(self, item: str) -> TranslationNamespace:
        return self._namespace[item]


def load_translations(
    *,
    translations: Optional[Translations] = None,
    scales: Optional[List[PrimitiveScale]] = None,
    translation_folder: str = "translations",
) -> NoReturn:
    """
    Loads translations from scales.

    Parameters
    ----------
    translations: Translations, optional
        The translations to load into (defaults to ``translations.t``)
    scales: List[PrimitiveScale], optional
        The scales to look at (defaults to ``Config.SCALES``).
    translation_folder: str
        The name of the translation folder.
    """
    if translations is None:
        translations = t

    if scales is None:
        scales = Config.SCALES

    for scale in scales:
        if (path := scale.path / translation_folder).is_dir():
            for lan in Config.LANGUAGE_AVAILABLE:
                if (path / f"{lan}.yml".lower()).is_file():
                    translations.register_translation_namespace(path.parent.name, path)


# global translations container
t = Translations()

# global translations namespace
t.register_translation_namespace("g", Path(__file__).parent / "translations")
