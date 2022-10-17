from __future__ import annotations


__all__ = ("Client",)


import attr
import copy
import inspect

from functools import partial
from typing import TYPE_CHECKING

from naff import (
    Client as nClient,
    BaseCommand as nBaseCommand,
    SlashCommand as nSlashCommand,
    Listener as nListener,
    Task as nTask,
    Embed as nEmbed,
    EmbedFooter as nEmbedFooter,
    Timestamp as nTimestamp,
)

from .colors import AllColors as Colors
from .database import db_wrapper
from .stats import try_increment
from .translations import t


if TYPE_CHECKING:
    from naff import (
        Context as nContext,
        PrefixedContext as nPrefixedContext,
        InteractionContext as nInteractionContext,
    )
    from typing import Callable


class Client(nClient):
    def __new__(cls, bot: nClient, *args, **kwargs):
        for name, member in inspect.getmembers(
            cls, predicate=lambda x: isinstance(x, (nBaseCommand, nListener, nTask))
        ):
            changes = {"callback": db_wrapper(member.callback)}

            if isinstance(member, nBaseCommand):
                if member.pre_run_callback:
                    changes["pre_run_callback"] = db_wrapper(member.pre_run_callback)
                if member.post_run_callback:
                    changes["post_run_callback"] = db_wrapper(member.post_run_callback)
                if member.error_callback:
                    changes["error_callback"] = db_wrapper(member.error_callback)
                else:
                    # apply the default error-handler
                    changes["error_callback"] = db_wrapper(cls.error)

            if isinstance(member, nSlashCommand):
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
                # nBaseCommand
                wrapped_member = attr.evolve(member, **changes)
            else:
                # nListener | nTask
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
        self: nClient
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

        return self

    async def error(self, e: Exception, ctx: nPrefixedContext | nInteractionContext, *_):
        """
        Basic error handler for commands.

        Coverage
        --------
        - AssertionError
            Displays the user that some input isn't correct.
        - NotImplementedError
            Displays the user that the command isn't implemented.
        """
        match e:
            case AssertionError():
                return await ctx.reply(
                    embed=nEmbed(
                        description=e.args[0],
                        timestamp=nTimestamp.now(),
                        footer=nEmbedFooter(
                            text=t.g.executed_by(user=ctx.author, id=ctx.author.id),
                            icon_url=ctx.author.display_avatar.url,
                        ),
                        color=Colors.assertion,
                    ),
                )
            case NotImplementedError():
                return await ctx.reply(
                    embed=nEmbed(
                        description=e.args[0],
                        timestamp=nTimestamp.now(),
                        footer=nEmbedFooter(
                            text=t.g.executed_by(user=ctx.author, id=ctx.author.id),
                            icon_url=ctx.author.display_avatar.url,
                        ),
                        color=Colors.notimplemented,
                    ),
                )
            case _:
                raise


async def pre_call_callback(self: nBaseCommand, callback: Callable, context: nContext):
    module = inspect.getmodule(self.extension or self.callback)
    await try_increment(module, context)
    return await self.call_callback(callback, context)
