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

_1337 = {
    "o": "0",
    "i": "1",
    "l": "1",
    "z": "2",
    "e": "3",
    "a": "4",
    "s": "5",
    # "g": "6" <-- "g" is set to "9"
    "t": "7",
    "b": "8",
    "g": "9"
}


def convert_to_1337(text, /):
    """
    this function converts a "normal"-text to a "1337"-text

    Parameters
    ----------
    text: :class:`str`
        the text with should be converted

    Returns
    -------
    :class:`str`
        the converted text
    """
    return "".join(
        [s if (sl := s.lower()) not in _1337 else _1337[sl]
         for s in text]
    )
