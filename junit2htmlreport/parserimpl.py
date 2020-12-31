"""
Parse results using junitparser
"""

from junitparser import JUnitXml


def load_report(filename):
    """
    Load a report from disjk
    """
    xml = JUnitXml.fromfile(filename)
    return xml


def load_string(text):
    """
    Load a report from a string
    """
    xml = JUnitXml.fromstring(text)
    return xml
