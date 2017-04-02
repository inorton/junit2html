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
        string = content.encode("utf-8")
        #string = content.encode('ascii', 'xmlcharrefreplace')
    return cgi.escape(string)

