from __future__ import annotations


__all__ = ("NoAliasEnum",)


import sys

from aenum import NoAliasEnum as aNoAliasEnum
from typing import TypeVar


T = TypeVar("T")


class NoAliasEnum(aNoAliasEnum):
    @property
    def scale(self) -> str:
        return sys.modules[self.__class__.__module__].__package__.rsplit(
            ".", maxsplit=1
        )[-1]

    @property
    def fullname(self) -> str:
        return "{0.scale}:{0.name}".format(self)

    @property
    def default(self) -> T:
        return self.value
