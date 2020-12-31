"""
Parse results files
"""
from .parser import Junit


def load_report(filename: str) -> Junit:
    """
    Load a report from disjk
    """
    return Junit(filename=filename)


def load_string(text: str) -> Junit:
    """
    Load a report from a string
    """
    return Junit(xmlstring=text)
