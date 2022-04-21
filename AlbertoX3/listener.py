from __future__ import annotations


__all__ = (
    "blocked_event_owner_event",
    "blocked_event_message_create",
    "blocked_event_message_update",
    "blocked_event_message_delete",
    "blocked_event_guild_member_add",
    "blocked_event_guild_member_update",
    "blocked_event_guild_member_remove",
    "event_contributor_event",
)


from asyncio import gather
from typing import TYPE_CHECKING, ParamSpec, TypeVar, Generic

from AlbertUnruhUtils.utils.logger import get_logger

from .database import db_context

# need to be defined here to have PUBSUB_FUNC only if TYPE_CHECKING
PUBSUB_ARGS = ParamSpec("PUBSUB_ARGS")
PUBSUB_RESULT = TypeVar("PUBSUB_RESULT")

if TYPE_CHECKING:
    from .adis_snek import Scale
    from typing import Callable, Awaitable, Optional, Type, List, NoReturn

    PUBSUB_FUNC = Callable[PUBSUB_ARGS, Awaitable[PUBSUB_RESULT | None]]


logger = get_logger(__name__.split(".")[-1], level=None, add_handler=False)


class Subscription(Generic[PUBSUB_ARGS, PUBSUB_RESULT]):
    channel: Channel
    _func: PUBSUB_FUNC
    _cls: Optional[Type[Scale]]

    def __init__(self, func: PUBSUB_FUNC):
        self._func = func
        self._cls = None

        self.channel.register(self)

    async def __call__(
        self, *args: PUBSUB_ARGS.args, **kwargs: PUBSUB_ARGS.kwargs
    ) -> PUBSUB_RESULT | None:
        if not self._cls.enabled:
            return None

        async with db_context():
            return await self._func(self._cls.instance, *args, **kwargs)

    def __set_name__(self, owner: Type[Scale], name):
        self._cls = owner


class Channel:
    _subscriptions: List[PUBSUB_FUNC]

    def __init__(self):
        self._subscriptions = []

    async def publish(
        self, *args: PUBSUB_ARGS.args, **kwargs: PUBSUB_ARGS.kwargs
    ) -> List[PUBSUB_RESULT]:
        result = await gather(*[sub(*args, **kwargs) for sub in self._subscriptions])
        return [r for r in result if r is not None]

    __call__ = publish

    @property
    def subscribe(self) -> Type[Subscription[PUBSUB_ARGS, PUBSUB_RESULT]]:
        class Sub(Subscription[PUBSUB_ARGS, PUBSUB_RESULT]):
            channel = self

        return Sub

    def register(
        self, subscription: Subscription[PUBSUB_ARGS, PUBSUB_RESULT]
    ) -> NoReturn:
        self._subscriptions.append(subscription)


# ****** public listener ****** #

# called when an event was blocked
blocked_event_owner_event = Channel()
blocked_event_message_create = Channel()
blocked_event_message_update = Channel()
blocked_event_message_delete = Channel()
blocked_event_guild_member_add = Channel()
blocked_event_guild_member_update = Channel()
blocked_event_guild_member_remove = Channel()

# called when an event was called
event_contributor_event = Channel()
