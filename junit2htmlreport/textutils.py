"""
Stringify to unicode
"""
import sys
__py3__ = sys.version_info > (3, 0)


def unicode_str(text):
    """
    Convert text to unicode
    :param text:
    :return:
    """
    if __py3__:
        if isinstance(text, bytes):
            return text.decode("utf-8", "strict")
        return str(text)
    return unicode(text)
