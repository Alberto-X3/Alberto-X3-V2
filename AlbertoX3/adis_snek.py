from __future__ import annotations


__all__ = ("Scale",)


from dis_snek import Scale as dScale, Snake as dSnake

from .database import db_wrapper


class Scale(dScale):
    def __new__(cls, bot: dSnake, *args, **kwargs):
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

        # commands
        for command in self.commands:
            # callback
            if command.callback is not None:
                command.callback = db_wrapper(command.callback)
            # pre_run_callback
            if command.pre_run_callback is not None:
                command.pre_run_callback = db_wrapper(command.pre_run_callback)
            # post_run_callback
            if command.post_run_callback is not None:
                command.post_run_callback = db_wrapper(command.post_run_callback)

        return self
