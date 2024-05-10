"""
Stringify to unicode
"""

from typing import Any, Optional


def unicode_str(text: "Optional[Any]"):
    """
    Convert text to unicode
    :param text:
    :return:
    """
    if isinstance(text, bytes):
        return text.decode("utf-8", "strict")
    return "" if text is None else str(text)
