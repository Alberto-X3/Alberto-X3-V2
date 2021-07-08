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
    "convert_normal_to_1337",
    "convert_1337_to_normal",
)


class Language:
    """
    Is the class for all Language-utils.
    """

    table = {
        "o": "0",
        "i": "1",
        "l": "1",
        "z": "2",
        "e": "3",
        "a": "4",
        "s": "5",
        "g": "6",
        "t": "7",
        "b": "8"
    }

    from .utils import reverse_dict as _r_d
    table_reversed = _r_d(table)

    def c_normal_to_1337(self, text, /):
        """
        This function converts a "normal"-text to a "1337"-text.

        Parameters
        ----------
        text: :class:`str`
            The text with should be converted.

        Returns
        -------
        :class:`str`
            The converted text.
        """
        t = self.table
        return "".join(
            [s if (sl := s.lower()) not in t else t[sl]
             for s in text]
        )

    def c_1337_to_normal(self, text, /):
        """
        This function converts a "1337"-text to a "normal"-text.

        Warnings
        --------
        This method has problems to differ between ``i`` and ``l`` and 'll
        convert it in every case to a ``i`` and the detection is not
        case sensitive!

        Parameters
        ----------
        text: :class:`str`
            The text with should be converted.

        Returns
        -------
        :class:`str`
            The converted text.
        """
        t = self.table_reversed
        return "".join(
            [s if (sl := s.lower()) not in t else t[sl]
             for s in text]
        )


Language = Language()

convert_normal_to_1337 = Language.c_normal_to_1337
convert_1337_to_normal = Language.c_1337_to_normal
