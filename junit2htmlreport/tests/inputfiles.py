"""
Helper for loading our test files
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))


def get_filepath(filename):
    """

    :param filename:
    :return:
    """
    return os.path.join(HERE, filename)
