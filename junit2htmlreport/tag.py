"""
Crude generation of HTML
"""

import cgi


def text(content):
    """
    Render content as escaped html text
    :param content:
    :return:
    """
    string = ""
    if content is not None:
        string = content
    return cgi.escape(string)
