"""
Render junit reports as HTML
"""
from . import tag


class HTMLRenderer(object):
    def __init__(self):
        self.tests = {}
        self.classes = {}
        self.suites = {}

        # if we have more than one report, we run in matrix mode
        # and generate a parent page and folder full of individual reports
        self.reports = {}

    def add_report(self, junit):
        """
        Add a report to be rendered
        """
        for suite in junit:
            pass