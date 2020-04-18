"""
Crude generation of HTML
"""

import sys
if sys.version_info >= (3, 0):
    from html import escape
else:
    from cgi import escape


def text(content):
    """
    Render content as escaped html text
    :param content:
    :return:
    """
    string = ""
    if content is not None:
        string = content
    return escape(string)
