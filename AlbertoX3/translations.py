__all__ = (
    "Translations",
    "merge",
    "load_translations",
    "t",
)


from AlbertUnruhUtils.utils.logger import get_logger
from pathlib import Path
from yaml import safe_load

from .config import Config
from .types import PrimitiveScale
from .utils import get_language


logger = get_logger(__name__.split(".")[-1])


def merge(
    base: dict,
    src: dict,
) -> dict:
    """
    Merges to dictionaries recursively.

    Parameters
    ----------
    base: dict
        The dictionary to merge into.
    src: dict
        The dictionary to merge into ``base``.

    Returns
    -------
    dict
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
    _fallback: dict

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


class TranslationNamespace:
    _sources: list[Path]
    _translations: dict[str, dict[str, ...]]

    def __init__(self):
        self._sources = []
        self._translations = {}

    def tn_add_source(self, source: Path):
        self._sources.append(source)
        self._translations.clear()

    def tn_get_language(self, lan: str) -> dict[str, ...]:
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
    _namespace: dict[str, TranslationNamespace]

    def __init__(self):
        self._namespace = {}

    def register_translation_namespace(self, name: str, file: Path):
        if name not in self._namespace:
            logger.debug(f"Creating TranslationNamespace for {name!r}")
            self._namespace[name] = TranslationNamespace()
        else:
            logger.debug(f"Extending TranslationNamespace for {name!r}")

        self._namespace[name].tn_add_source(file)

    def __getattr__(self, item: str):
        return self._namespace[item]


def load_translations(
    *,
    translations: Translations = None,
    scales: list[PrimitiveScale] = None,
    translation_folder: str = "translations",
) -> None:
    """
    Loads translations from scales.

    Parameters
    ----------
    translations: Translations, optional
        The translations to load into (defaults to ``translations.t``)
    scales: list[PrimitiveScale], optional
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
