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
        # Convert unicode str to bytes in Python 2
        # Python 3 is using unicode natively
        string = content
        try:
            if isinstance(content, unicode):
                string = content.encode("utf-8")
        except:
            pass
        #string = content.encode('ascii', 'xmlcharrefreplace')
    return cgi.escape(string)
