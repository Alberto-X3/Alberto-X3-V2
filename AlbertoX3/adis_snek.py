from __future__ import annotations


__all__ = ("Scale",)


import attr
import copy
import inspect

from functools import partial
from typing import TYPE_CHECKING

from dis_snek import (
    Scale as dScale,
    BaseCommand as dBaseCommand,
    SlashCommand as dSlashCommand,
    Listener as dListener,
    Task as dTask,
    Embed as dEmbed,
    EmbedFooter as dEmbedFooter,
    Timestamp as dTimestamp,
)

from .colors import AllColors as Colors
from .database import db_wrapper
from .stats import try_increment
from .translations import t


if TYPE_CHECKING:
    from dis_snek import (
        Snake as dSnake,
        Context as dContext,
        MessageContext as dMessageContext,
        InteractionContext as dInteractionContext,
    )
    from typing import Callable


class Scale(dScale):
    enabled: bool = True
    instance: Scale

    def __new__(cls, bot: dSnake, *args, **kwargs):
        # whether it was already initialized
        if getattr(cls, "instance", None) is not None:
            return cls.instance

        for name, member in inspect.getmembers(
            cls, predicate=lambda x: isinstance(x, (dBaseCommand, dListener, dTask))
        ):
            changes = {"callback": db_wrapper(member.callback)}

            if isinstance(member, dBaseCommand):
                if member.pre_run_callback:
                    changes["pre_run_callback"] = db_wrapper(member.pre_run_callback)
                if member.post_run_callback:
                    changes["post_run_callback"] = db_wrapper(member.post_run_callback)
                if member.error_callback:
                    changes["error_callback"] = db_wrapper(member.error_callback)
                else:
                    # apply the default error-handler
                    changes["error_callback"] = db_wrapper(cls.error)

            if isinstance(member, dSlashCommand):
                if member.autocomplete_callbacks:
                    autocomplete_callbacks = {
                        name: db_wrapper(call)
                        for name, call in member.autocomplete_callbacks.items()
                    }
                    changes["autocomplete_callbacks"] = autocomplete_callbacks
                if member.options:
                    options = []
                    for opt in member.options:
                        if opt not in getattr(member.callback, "options", []):
                            options.append(opt)
                    changes["options"] = options

            if attr.has(member.__class__):
                # dBaseCommand
                wrapped_member = attr.evolve(member, **changes)
            else:
                # dListener | dTask
                wrapped_member = copy.copy(member)
                for change in changes:
                    setattr(wrapped_member, change, changes[change])

            if hasattr(wrapped_member, "call_callback"):
                # run `pre_call_callback` and after that `call_callback`
                #
                # has to be `member`, otherwise we 'll have recursion
                wrapped_member.call_callback = partial(pre_call_callback, member)

            setattr(cls, name, wrapped_member)

        # super-call is here since it registers all callbacks from the commands etc.
        self = super().__new__(cls, bot, *args, **kwargs)

        # checks
        scale_checks = []
        for check in self.scale_checks:
            scale_checks.append(db_wrapper(check))
        self.scale_checks = scale_checks

        # prerun
        scale_prerun = []
        for prerun in self.scale_prerun:
            scale_prerun.append(db_wrapper(prerun))
        self.scale_prerun = scale_prerun

        # postrun
        scale_postrun = []
        for postrun in self.scale_postrun:
            scale_prerun.append(db_wrapper(postrun))
        self.scale_postrun = scale_postrun

        # listeners
        for listener in self.listeners:
            listener.callback = db_wrapper(listener.callback)

        self.instance = self

        return self

    def __delete__(self, instance):
        # "un-"init
        del self.instance

    async def error(self, e: Exception, ctx: dMessageContext | dInteractionContext, *_):
        """
        Basic error handler for commands.

        Coverage
        --------
        - AssertionError
            Displays the user that some input isn't correct.
        - NotImplementedError
            Displays the user that the command isn't implemented.
        """
        if isinstance(e, AssertionError):
            return await ctx.reply(
                embed=dEmbed(
                    description=e.args[0],
                    timestamp=dTimestamp.now(),
                    footer=dEmbedFooter(
                        text=t.g.executed_by(user=ctx.author, id=ctx.author.id),
                        icon_url=ctx.author.display_avatar.url,
                    ),
                    color=Colors.assertion,
                ),
            )
        elif isinstance(e, NotImplementedError):
            return await ctx.reply(
                embed=dEmbed(
                    description=e.args[0],
                    timestamp=dTimestamp.now(),
                    footer=dEmbedFooter(
                        text=t.g.executed_by(user=ctx.author, id=ctx.author.id),
                        icon_url=ctx.author.display_avatar.url,
                    ),
                    color=Colors.notimplemented,
                ),
            )
        else:
            raise


async def pre_call_callback(self: dBaseCommand, callback: Callable, context: dContext):
    module = inspect.getmodule(self.scale or self.callback)
    await try_increment(module, context)
    return await self.call_callback(callback, context)
