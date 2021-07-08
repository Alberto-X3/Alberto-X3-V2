"""
MIT License

Copyright (c) 2021 AlbertUnruh

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__all__ = (
    "docs",
    "register_cogs",
    "reverse_dict"
)


class Utils:
    """
    Is the class for all Utils.
    """

    @staticmethod
    def docs(original, /):
        """
        Copies the documentation from a :class:`object`.

        Parameters
        ----------
        original: :class:`object`, :class:`str`
            The object from which the docs should be copied.

        Returns
        -------
        :class:`Callable[[:class:`object`], :class:`object`]`
            The actual decorator.
        """
        if not isinstance(original, str):
            original = original.__doc__

        def decorator(overridden):
            """
            Is the actual decorator to override the docs.

            Parameters
            ----------
            overridden: :class:`object`
                The actual object where the docs should be overridden
                by :arg:`doc`.

            Returns
            -------
            :class:`object`
                The object with the overridden docs.
            """
            overridden.__doc__ = original
            return overridden
        return decorator

    @staticmethod
    def register_cogs(bot, *cogs):
        """
        Registers the cogs on the bot.

        Parameters
        ----------
        bot: :class:`discord.extension.commands.Bot`
            The bot on which the :arg:`cogs` should be registered.
        *cogs: :class:`discord.extension.commands.Cog`
            The cogs which should be registered on the :arg:`bot`.
        """
        raise NotImplementedError

    @staticmethod
    def reverse_dict(to_reverse, /):
        """
        Reverses a dictionary.

        Parameters
        ----------
        to_reverse: :class:`dict[KT, VT]`
            The dictionary which should be reversed.

        Returns
        -------
        :class:`dict[VT, KT]`
            The reversed dictionary.
        """
        new = {}
        for k in to_reverse:
            new.setdefault(to_reverse[k], k)
        return new


Utils = Utils()

docs = Utils.docs
register_cogs = Utils.register_cogs
reverse_dict = Utils.reverse_dict
