from __future__ import annotations


__all__ = ("Contributor",)


from aenum import NoAliasEnum
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import Optional, Tuple, FrozenSet


_FALSE_DATA: FrozenSet[str, ...] = frozenset(
    {"0", "-1", "none", "nan", "false", "/", "()", "[]", "{}", "set()"}
)


class ContributorEnum(NoAliasEnum):
    name: str

    @property
    def discord_id(self) -> Optional[int]:
        if str(ret := self.value[0]).lower() in _FALSE_DATA:
            ret = None
        return ret

    @property
    def discord_mention(self) -> Optional[str]:
        return f"<@{self.discord_id}>" if self.discord_id else None

    @property
    def github(self) -> Tuple[Optional[int], Optional[str]]:
        if str(tmp := self.value[1]).lower() in _FALSE_DATA:
            return None, None
        tmp: Tuple[str, ...] = tuple(map(str, tmp))
        assert (
            len(tmp) == 2
        ), f"Invalid GitHub ID/Node-ID {tmp!r}! Expected 'Tuple[int, str]'"
        ret = ()
        if tmp[0] not in _FALSE_DATA and tmp[0].isnumeric():
            ret += (int(tmp[0]),)
        else:
            ret += (None,)
        if tmp[1] not in _FALSE_DATA:
            ret += (tmp[1],)
        else:
            ret += (None,)
        return ret  # type: ignore

    @property
    def github_id(self) -> Optional[int]:
        return self.github[0]

    @property
    def github_node_id(self) -> Optional[str]:
        return self.github[1]


class Contributor(ContributorEnum):
    # (Discord ID, (GitHub ID, GitHub Node-ID))
    AlbertUnruh = (546320163276849162, (73029826, "MDQ6VXNlcjczMDI5ODI2"))
