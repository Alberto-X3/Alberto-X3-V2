from __future__ import annotations


__all__ = (
    "Quiz",
    "setup",
)


from typing import TYPE_CHECKING

from dis_snek import (
    message_command,
    Embed,
    EmbedFooter,
    Timestamp,
)

from AlbertoX3.adis_snek import Scale
from AlbertoX3.translations import t

from .colors import Colors
from .models import YesNoModel, QuadChoiceModel


if TYPE_CHECKING:
    from dis_snek import MessageContext, Snake


tg = t.g
t = t.quiz


class Quiz(Scale):
    ...


def setup(bot: Snake):
    Quiz(bot)
