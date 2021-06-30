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


def copy_doc(original):
    """
    copies the documentation from a :class:`object`

    Parameters
    ----------
    original: :class:`object`
        the object from which the docs should be copied

    Returns
    -------
    :class:`~typing.Callable[[:class:`object`], :class:`object`]`
        the actual decorator
    """
    def decorator(overridden):
        """
        is the actual decorator to override the docs

        Parameters
        ----------
        overridden: :class:`object`
            the actual object where the docs should be overridden
            by :arg:`original`

        Returns
        -------
        :class:`object`
            the object with the overridden docs
        """
        overridden.__doc__ = original.__doc__
        return overridden

    return decorator


register_cogs = NotImplemented
register_cogs.__doc__ = """
    registers the cogs on the bot

    Parameters
    ----------
    bot: :class:`~discordX3.extension.commands.Bot`
    *cogs: :class:`~discordX3.extension.commands.Cog`
    """
