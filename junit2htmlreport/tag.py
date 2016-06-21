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
    return cgi.escape(str(content))

