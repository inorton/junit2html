"""
Helper for loading our test files
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))


def get_reports():
    return [x for x in os.listdir(HERE) if x.endswith(".xml")]


def get_filepath(filename):
    """

    :param filename:
    :return:
    """
    return os.path.join(HERE, filename)
