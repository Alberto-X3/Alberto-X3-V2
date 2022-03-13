__all__ = (
    "Quiz",
    "setup",
)


from dis_snek import (
    Snake,
    message_command,
    MessageContext,
    Embed,
    EmbedFooter,
    Timestamp,
)

from AlbertoX3.adis_snek import Scale
from AlbertoX3.translations import t

from .colors import Colors
from .models import YesNoModel, QuadChoiceModel


tg = t.g
t = t.quiz


class Quiz(Scale):
    ...


def setup(bot: Snake):
    Quiz(bot)
