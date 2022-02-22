__all__ = (
    "Translations",
    "merge",
)


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


class Translations:
    FALLBACK: str = "EN"
