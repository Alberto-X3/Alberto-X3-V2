from __future__ import annotations


__all__ = (
    "FormatStr",
    "PrimitiveScale",
)


from pathlib import Path
from typing import NamedTuple


class FormatStr(str):
    __call__ = str.format


PrimitiveScale = NamedTuple(
    "PrimitiveScale", (("name", str), ("package", str), ("path", Path))
)
