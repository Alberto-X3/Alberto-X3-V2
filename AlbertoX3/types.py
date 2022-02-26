__all__ = ("PrimitiveScale",)


from pathlib import Path
from typing import NamedTuple


PrimitiveScale = NamedTuple(
    "PrimitiveScale", (("name", str), ("package", str), ("path", Path))
)
