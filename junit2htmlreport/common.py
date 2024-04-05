"""
Common code between JUnit2HTML matrix and merge classes
"""
from __future__ import print_function

from .parser import Case, Junit


class ReportContainer(object):
    """
    Hold one or more reports
    """
    reports: dict[str, Junit]

    def __init__(self):
        self.reports = {}

    def add_report(self, filename: str) -> None:
        raise NotImplementedError()

    def failures(self):
        """
        Return all the failed test cases
        :return:
        """
        found: list[Case] = []
        for report in self.reports:
            for suite in self.reports[report].suites:
                found.extend(suite.failed())

        return found

    def skips(self):
        """
        Return all the skipped test cases
        :return:
        """
        found: list[Case] = []
        for report in self.reports:
            for suite in self.reports[report].suites:
                found.extend(suite.skipped())
        return found