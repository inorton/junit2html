"""
Stringify to unicode
"""

from typing import Any


def unicode_str(text: Any|None):
    """
    Convert text to unicode
    :param text:
    :return:
    """
    if isinstance(text, bytes):
        return text.decode("utf-8", "strict")
    return "" if text is None else str(text)
